from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .db import connect
from .normalise import parse_datetime, utc_now
from .provider_manager import ProviderManager
from .repository import Repository

MAX_COLLECTION_DAYS = 31


class _JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_json_ld = False
        self._parts: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attributes = {key.lower(): value for key, value in attrs}
        self._in_json_ld = (
            (attributes.get("type") or "").split(";", 1)[0].strip().lower()
            == "application/ld+json"
        )
        if self._in_json_ld:
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_json_ld:
            self.blocks.append("".join(self._parts))
            self._parts = []
            self._in_json_ld = False


def _walk_json_ld(value: Any):
    if isinstance(value, list):
        for item in value:
            yield from _walk_json_ld(item)
    elif isinstance(value, dict):
        types = value.get("@type", [])
        if isinstance(types, str):
            types = [types.rsplit("/", 1)[-1]]
        if any(str(item).rsplit("/", 1)[-1] == "SportsEvent" for item in types):
            yield value
        for key, child in value.items():
            if key in {"homeTeam", "awayTeam", "superEvent", "competition", "tournament", "league", "organizer"}:
                continue
            if isinstance(child, (list, dict)):
                yield from _walk_json_ld(child)


def _name(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        candidate = value.get("name")
        return str(candidate).strip() if candidate else None
    return None


def _identifier(value: Any) -> str | None:
    if isinstance(value, (str, int)):
        return str(value)
    if isinstance(value, dict):
        candidate = value.get("value") or value.get("name") or value.get("@id")
        return str(candidate) if candidate else None
    return None


def _competition(event: dict[str, Any]) -> str | None:
    for key in ("superEvent", "competition", "tournament", "league", "organizer"):
        value = event.get(key)
        if isinstance(value, list):
            names = [_name(item) for item in value]
            value = next((name for name in names if name), None)
        else:
            value = _name(value)
        if value:
            return value
    return None


class SchemaOrgHtmlCollector:
    """Parse saved, permitted HTML containing Schema.org SportsEvent JSON-LD."""

    key = "sports_event_html"

    def parse(
        self,
        html: str,
        *,
        source_url: str | None = None,
        source_key: str | None = None,
        competition: str | None = None,
        source_name: str = "saved-html",
    ) -> dict[str, Any]:
        if source_url:
            parsed_url = urlparse(source_url)
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                raise ValueError("source_url must be an absolute HTTP(S) URL")

        parser = _JsonLdParser()
        parser.feed(html)
        events: list[dict[str, Any]] = []
        errors: list[str] = []
        for block_index, block in enumerate(parser.blocks, start=1):
            try:
                events.extend(_walk_json_ld(json.loads(block)))
            except json.JSONDecodeError as exc:
                errors.append(f"JSON-LD block {block_index} is invalid: {exc.msg}.")

        raw_digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
        records: list[dict[str, Any]] = []
        for index, event in enumerate(events, start=1):
            try:
                home = _name(event.get("homeTeam"))
                away = _name(event.get("awayTeam"))
                kickoff = parse_datetime(event.get("startDate"))
                event_competition = competition or _competition(event)
                if not home or not away:
                    raise ValueError("homeTeam and awayTeam are required")
                if not event_competition:
                    raise ValueError("competition is missing; supply --competition when it is known")

                status_value = str(event.get("eventStatus") or "").lower()
                status = (
                    "finished"
                    if "completed" in status_value or "finished" in status_value
                    else "cancelled" if "cancelled" in status_value else "scheduled"
                )
                record: dict[str, Any] = {
                    "external_id": _identifier(event.get("identifier")) or event.get("@id"),
                    "competition": event_competition,
                    "season": _identifier(event.get("season")),
                    "kickoff_utc": kickoff,
                    "home_team": home,
                    "away_team": away,
                    "status": status,
                    "source_key": source_key or self.key,
                    "source_ref": (
                        _identifier(event.get("identifier"))
                        or event.get("@id")
                        or event.get("url")
                        or f"{raw_digest}:{index}"
                    ),
                    "source_url": event.get("url") or source_url,
                    "collected_at": utc_now(),
                    "provider_payload": {
                        "format": "schema.org SportsEvent JSON-LD",
                        "source_name": source_name,
                        "source_html_sha256": raw_digest,
                        "event": event,
                    },
                }
                home_score, away_score = event.get("homeScore"), event.get("awayScore")
                if home_score is not None and away_score is not None:
                    record["home_score"] = int(home_score)
                    record["away_score"] = int(away_score)
                    record["status"] = "finished"
                if event.get("additionalProperty") is not None:
                    record["statistics"] = event["additionalProperty"]
                records.append(record)
            except (TypeError, ValueError) as exc:
                errors.append(f"SportsEvent {index} was skipped: {exc}.")

        if not events and not errors:
            errors.append("No Schema.org SportsEvent JSON-LD was found.")
        return {
            "source": source_key or self.key,
            "source_url": source_url,
            "records": records,
            "records_collected": len(records),
            "errors": errors,
            "status": "success" if records and not errors else ("partial" if records else "failed"),
            "authority": "structured_saved_html_only",
        }

    def collect_file(
        self,
        path: Path | str,
        *,
        source_url: str | None = None,
        source_key: str | None = None,
        competition: str | None = None,
    ) -> dict[str, Any]:
        file_path = Path(path)
        html = file_path.read_text(encoding="utf-8")
        return self.parse(
            html,
            source_url=source_url,
            source_key=source_key,
            competition=competition,
            source_name=file_path.name,
        )


class CollectionCoordinator:
    """Coordinate configured API providers and local structured-HTML ingestion."""

    UNAVAILABLE_PROVIDER_DETAILS = {
        "football_data_co_uk": "No adapter; commercial and AI/data-training restrictions require rights review.",
        "clearsports": "No current adapter is registered.",
        "the_odds_api": "No current adapter is registered.",
        "openweather": "No current adapter is registered.",
    }
    DAILY_PROVIDERS = {
        "api_football",
        "livefootball",
        "sportmonks",
        "sportscore",
        "thesportsdb",
    }
    RANGE_PROVIDERS = {"footballdata_io", "football_data_org", "openligadb"}

    def __init__(
        self,
        repo: Repository | None = None,
        providers: ProviderManager | None = None,
    ) -> None:
        self.repo = repo or Repository()
        self.providers = providers or ProviderManager(self.repo)

    def catalog(self) -> list[dict[str, Any]]:
        provider_rows = self.providers.catalog()
        result = [
            {
                "key": row["key"],
                "kind": "local_file" if row.get("kind") == "local_csv" else "api",
                "available": row["key"] in self.providers.adapter_classes,
                "enabled": bool(row["enabled"]),
                "status": (
                    "not_integrated"
                    if row["key"] not in self.providers.adapter_classes
                    else "enabled" if row["enabled"] else "disabled"
                ),
                "description": row.get("description") or self.UNAVAILABLE_PROVIDER_DETAILS.get(row["key"], ""),
            }
            for row in provider_rows
        ]
        result.extend(
            [
                {
                    "key": "sports_event_html",
                    "kind": "local_html",
                    "available": True,
                    "enabled": True,
                    "status": "local_only",
                    "description": "Parse saved HTML with Schema.org SportsEvent JSON-LD; no network access.",
                },
                {
                    "key": "csv_json_import",
                    "kind": "local_file",
                    "available": True,
                    "enabled": True,
                    "status": "implemented",
                    "description": "Import local CSV or JSON through the existing archive importer.",
                },
                *[
                    {
                        "key": key,
                        "kind": "website",
                        "available": False,
                        "enabled": False,
                        "status": "not_integrated",
                        "description": description,
                    }
                    for key, description in (
                        ("soccerway", "No live collector; automated scraping requires express permission."),
                        ("flashscore", "No adapter; terms restrict personal use and database extraction."),
                        ("fotmob", "No adapter; robots.txt disallows general automated access to /api/."),
                        ("sofascore", "No adapter; undocumented endpoints are not used."),
                        ("official_competition_sites", "Access and reuse terms vary; no site-specific adapter is verified."),
                    )
                ],
            ]
        )
        return result

    def collect_sources(
        self,
        sources: list[str],
        *,
        date_from: str,
        date_to: str,
        competition: str | None = None,
        league: str | None = None,
        season: str | None = None,
        status: str | None = None,
        force_refresh: bool = False,
        cache_ttl_seconds: int = 900,
    ) -> dict[str, Any]:
        start = date.fromisoformat(date_from)
        end = date.fromisoformat(date_to)
        if end < start:
            raise ValueError("date_to must be on or after date_from")
        days = (end - start).days + 1
        if days > MAX_COLLECTION_DAYS:
            raise ValueError(f"Collection range is limited to {MAX_COLLECTION_DAYS} days per job.")
        if not sources:
            raise ValueError("Select one or more collectors explicitly.")

        results = []
        for requested_source in sources:
            source = requested_source.strip().lower()
            if not source:
                continue
            try:
                results.append(
                    self._collect_one(
                        source,
                        start,
                        end,
                        competition,
                        league,
                        season,
                        status,
                        force_refresh,
                        cache_ttl_seconds,
                    )
                )
            except Exception as exc:
                results.append(
                    {
                        "provider": source,
                        "status": "failed",
                        "records_received": 0,
                        "requests": [],
                        "message": f"{type(exc).__name__}: {exc}",
                    }
                )
        successful = sum(result["status"] in {"success", "empty"} for result in results)
        failed = len(results) - successful
        return {
            "status": "success" if results and not failed else ("partial" if successful else "failed"),
            "sources_requested": len(results),
            "sources_succeeded": successful,
            "sources_failed": failed,
            "records_received": sum(result["records_received"] for result in results),
            "results": results,
        }

    def _collect_one(
        self,
        source: str,
        start: date,
        end: date,
        competition: str | None,
        league: str | None,
        season: str | None,
        status: str | None,
        force_refresh: bool,
        cache_ttl_seconds: int,
    ) -> dict[str, Any]:
        if source in self.DAILY_PROVIDERS:
            requests = []
            for offset in range((end - start).days + 1):
                kwargs: dict[str, Any] = {
                    "date": (start + timedelta(days=offset)).isoformat(),
                    "force_refresh": force_refresh,
                    "cache_ttl_seconds": cache_ttl_seconds,
                }
                if source == "api_football":
                    kwargs.update(league=league or competition, season=season, status=status)
                elif source == "sportscore":
                    kwargs.update(competition=competition, status=status or "upcoming")
                elif source == "thesportsdb":
                    kwargs.update(league=league or competition)
                requests.append(self.providers.fetch(source, **kwargs))
        elif source in self.RANGE_PROVIDERS:
            kwargs: dict[str, Any] = {
                "date_from": start.isoformat(),
                "date_to": end.isoformat(),
                "force_refresh": force_refresh,
                "cache_ttl_seconds": cache_ttl_seconds,
            }
            if source == "openligadb":
                kwargs.update(league=league or "", season=season or "")
            else:
                kwargs["competition"] = competition
            requests = [self.providers.fetch(source, **kwargs)]
        else:
            requests = [
                self.providers.fetch(
                    source,
                    date_from=start.isoformat(),
                    date_to=end.isoformat(),
                    force_refresh=force_refresh,
                    cache_ttl_seconds=cache_ttl_seconds,
                )
            ]

        received = sum(int(result.get("records_received", 0)) for result in requests)
        successful = sum(result.get("status") in {"success", "empty"} for result in requests)
        failed = len(requests) - successful
        return {
            "provider": source,
            "status": "success" if not failed and received else ("empty" if not failed else ("partial" if successful else "failed")),
            "records_received": received,
            "requests": requests,
            "message": f"{successful} request(s) succeeded; {failed} failed; {received} record(s) received.",
        }

    def collect_html_file(
        self,
        path: Path | str,
        *,
        source_url: str | None = None,
        source_key: str = "sports_event_html",
        competition: str | None = None,
    ) -> dict[str, Any]:
        started = utc_now()
        conn = connect(self.repo.db_path)
        try:
            cur = conn.execute(
                "INSERT INTO provider_runs(provider_key,started_at,status,metadata_json) VALUES(?,?,?,?)",
                (source_key, started, "running", "{}"),
            )
            run_id = int(cur.lastrowid)
            conn.commit()
        finally:
            conn.close()

        archived = 0
        received = 0
        errors: list[str] = []
        run_status = "failed"
        message = ""
        try:
            parsed = SchemaOrgHtmlCollector().collect_file(
                path,
                source_url=source_url,
                source_key=source_key,
                competition=competition,
            )
            received = int(parsed["records_collected"])
            errors.extend(parsed["errors"])
            for record in parsed["records"]:
                try:
                    self.repo.add_fixture(
                        record,
                        source_key=source_key,
                        source_ref=record["source_ref"],
                        source_url=record.get("source_url"),
                        raw_payload=record["provider_payload"],
                    )
                    archived += 1
                except (TypeError, ValueError, KeyError) as exc:
                    errors.append(f"Could not archive {record.get('source_ref')}: {exc}")
            run_status = "success" if archived and not errors else ("partial" if archived else "failed")
            message = f"Archived {archived} structured record(s) from saved HTML."
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            message = errors[-1]
        finally:
            conn = connect(self.repo.db_path)
            try:
                conn.execute(
                    "UPDATE provider_runs SET finished_at=?,status=?,records_received=?,message=? WHERE id=?",
                    (utc_now(), run_status, received, message, run_id),
                )
                conn.commit()
            finally:
                conn.close()
        return {
            "source": source_key,
            "status": run_status,
            "records_received": received,
            "records_archived": archived,
            "errors": errors,
            "message": message,
        }

    def recent_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        conn = connect(self.repo.db_path)
        try:
            rows = conn.execute(
                "SELECT id,provider_key,started_at,finished_at,status,records_received,message "
                "FROM provider_runs ORDER BY id DESC LIMIT ?",
                (max(1, min(int(limit), 500)),),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def provenance(self, fixture_id: int) -> dict[str, Any]:
        fixture = self.repo.get_fixture(fixture_id)
        if fixture is None:
            raise ValueError(f"Fixture {fixture_id} does not exist.")
        conn = connect(self.repo.db_path)
        try:
            snapshots = conn.execute(
                "SELECT source_key,source_ref,source_url,captured_at,payload_sha256,quality_label "
                "FROM source_snapshots WHERE fixture_id=? ORDER BY captured_at DESC",
                (fixture_id,),
            ).fetchall()
            observations = conn.execute(
                "SELECT field_name,value_json,source_key,source_ref,source_url,captured_at,verification_status "
                "FROM field_observations WHERE fixture_id=? ORDER BY captured_at DESC",
                (fixture_id,),
            ).fetchall()
            return {
                "fixture": fixture,
                "snapshots": [dict(row) for row in snapshots],
                "observations": [
                    {**dict(row), "value": json.loads(row["value_json"])} for row in observations
                ],
            }
        finally:
            conn.close()

    def coverage(self, date_from: str, date_to: str, competition: str | None = None) -> dict[str, Any]:
        start = date.fromisoformat(date_from)
        end = date.fromisoformat(date_to)
        if end < start:
            raise ValueError("date_to must be on or after date_from")
        days = (end - start).days + 1
        if days > 3660:
            raise ValueError("Coverage ranges are limited to 3660 days.")

        conn = connect(self.repo.db_path)
        try:
            rows = conn.execute(
                """SELECT substr(f.kickoff_utc,1,10) AS day,COUNT(DISTINCT f.id) AS fixtures,
                    GROUP_CONCAT(DISTINCT s.source_key) AS sources
                   FROM fixtures f LEFT JOIN source_snapshots s ON s.fixture_id=f.id
                   WHERE substr(f.kickoff_utc,1,10) BETWEEN ? AND ?
                     AND (? IS NULL OR f.competition=?)
                   GROUP BY day ORDER BY day""",
                (start.isoformat(), end.isoformat(), competition, competition),
            ).fetchall()
        finally:
            conn.close()

        by_day = {row["day"]: dict(row) for row in rows}
        coverage_days = [
            by_day.get(
                (start + timedelta(days=offset)).isoformat(),
                {"day": (start + timedelta(days=offset)).isoformat(), "fixtures": 0, "sources": None},
            )
            for offset in range(days)
        ]
        missing = [row["day"] for row in coverage_days if row["fixtures"] == 0]
        return {
            "date_from": start.isoformat(),
            "date_to": end.isoformat(),
            "competition": competition,
            "days": coverage_days,
            "days_without_fixtures": missing,
            "records_collected": sum(row["fixtures"] for row in coverage_days),
        }
