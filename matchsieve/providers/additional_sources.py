from __future__ import annotations

import os
from datetime import date as date_type
from typing import Any

from .base import ProviderError
from .http_json import get_json

def _rows(payload: Any, source: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = None
        for key in ("data", "fixtures", "matches", "results", "response"):
            value = payload.get(key)
            if isinstance(value, list):
                rows = value
                break
            if isinstance(value, dict):
                for nested in ("data", "fixtures", "matches", "results"):
                    if isinstance(value.get(nested), list):
                        rows = value[nested]
                        break
                if rows is not None:
                    break
        if rows is None:
            raise ProviderError(f"{source} returned HTTP success but no recognised fixture list; response schema needs mapping.")
    else:
        raise ProviderError(f"{source} returned an unexpected JSON type.")
    return [row for row in rows if isinstance(row, dict)]

def _team(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("name", "title", "team_name", "short_name", "displayName"):
            if value.get(key):
                return str(value[key]).strip()
    return None

def _normalise(row: dict[str, Any], source: str) -> dict[str, Any] | None:
    home = _team(row.get("home_team") or row.get("homeTeam") or row.get("home") or row.get("localteam") or row.get("participant_home"))
    away = _team(row.get("away_team") or row.get("awayTeam") or row.get("away") or row.get("visitorteam") or row.get("participant_away"))
    kickoff = row.get("kickoff_utc") or row.get("utcDate") or row.get("start_time") or row.get("startTime") or row.get("match_date") or row.get("date") or row.get("starting_at")
    if not home or not away or not kickoff:
        return None
    competition = row.get("competition") or row.get("league") or row.get("tournament") or row.get("competition_name") or "Unknown competition"
    if isinstance(competition, dict):
        competition = competition.get("name") or competition.get("title") or competition.get("short_name") or "Unknown competition"
    result: dict[str, Any] = {
        "external_id": row.get("id") or row.get("fixture_id") or row.get("match_id") or row.get("event_id"),
        "competition": str(competition),
        "season": row.get("season"),
        "kickoff_utc": str(kickoff),
        "home_team": home,
        "away_team": away,
        "status": str(row.get("status") or row.get("state") or "scheduled").lower(),
        "source_key": source,
        "source_url": {"sportmonks": "https://www.sportmonks.com/", "footballdata_io": "https://footballdata.io/", "livefootball": "https://live-football-api.com/"}[source],
        "quality_label": "source-reported-unreviewed",
        "provider_payload": row,
    }
    scores = row.get("score") if isinstance(row.get("score"), dict) else {}
    home_score = row.get("home_score", row.get("homeScore", scores.get("home")))
    away_score = row.get("away_score", row.get("awayScore", scores.get("away")))
    if home_score is not None and away_score is not None:
        try:
            result["home_score"], result["away_score"] = int(home_score), int(away_score)
        except (TypeError, ValueError):
            pass
    return result

class FootballDataIOProvider:
    key = "footballdata_io"
    base_url = "https://footballdata.io/api/v1"
    def fetch_fixtures(self, date_from: str, date_to: str, **kwargs: Any) -> list[dict[str, Any]]:
        token = os.getenv("FOOTBALLDATA_IO_API_KEY", "").strip()
        if not token:
            raise ProviderError("Set FOOTBALLDATA_IO_API_KEY in local .env before using FootballData.io.")
        if date_from != date_to:
            raise ProviderError("FootballData.io adapter currently accepts one date per fetch.")
        today = date_type.today().isoformat()
        if date_from < today:
            raise ProviderError("FootballData.io tested endpoints do not establish historical-date support; refusing to return today's fixtures for a past date.")
        endpoint = "fixtures/today" if date_from == today else "fixtures/upcoming"
        payload = get_json(f"{self.base_url}/{endpoint}", headers={"Authorization": f"Bearer {token}"})
        rows = _rows(payload, "FootballData.io")
        mapped = [_normalise(row, self.key) for row in rows]
        usable = [row for row in mapped if row is not None]
        if rows and not usable:
            raise ProviderError("FootballData.io returned records, but their fixture fields did not match the current mapper; no records archived.")
        return usable

class LiveFootballProvider:
    key = "livefootball"
    base_url = "https://live-football-api.com/api/v1"
    def fetch_fixtures(self, date: str, **kwargs: Any) -> list[dict[str, Any]]:
        token = os.getenv("LIVEFOOTBALL_API_KEY", "").strip()
        if not token:
            raise ProviderError("Set LIVEFOOTBALL_API_KEY in local .env before using LiveFootball.")
        payload = get_json(f"{self.base_url}/matches", params={"api_key": token, "date": date})
        rows = _rows(payload, "LiveFootball")
        mapped = [_normalise(row, self.key) for row in rows]
        usable = [row for row in mapped if row is not None]
        if rows and not usable:
            raise ProviderError("LiveFootball returned records, but their fixture fields did not match the current mapper; no records archived.")
        return usable

class SportMonksProvider:
    key = "sportmonks"
    base_url = "https://api.sportmonks.com/v3/football"
    def fetch_fixtures(self, date: str, **kwargs: Any) -> list[dict[str, Any]]:
        token = os.getenv("SPORTMONKS_API_TOKEN", "").strip()
        if not token:
            raise ProviderError("Set SPORTMONKS_API_TOKEN in local .env before using SportMonks.")
        payload = get_json(f"{self.base_url}/fixtures/date/{date}", params={"api_token": token, "include": "participants;scores;league"})
        rows = _rows(payload, "SportMonks")
        mapped = []
        for row in rows:
            # SportMonks v3 uses participants arrays; map them explicitly when present.
            participants = row.get("participants")
            if isinstance(participants, list):
                for participant in participants:
                    if not isinstance(participant, dict):
                        continue
                    meta = participant.get("meta") or {}
                    location = str(meta.get("location") or "").lower()
                    if location in ("home", "away"):
                        row["home_team" if location == "home" else "away_team"] = participant.get("name")
            scores = row.get("scores")
            if isinstance(scores, list):
                for score in scores:
                    if not isinstance(score, dict):
                        continue
                    description = str((score.get("description") or score.get("type") or {}).get("name", "") if isinstance(score.get("description") or score.get("type"), dict) else score.get("description") or score.get("type") or "").lower()
                    participant = str(score.get("score", {}).get("participant", "") if isinstance(score.get("score"), dict) else "").lower()
                    value = score.get("score", {}).get("goals") if isinstance(score.get("score"), dict) else score.get("goals")
                    if value is not None and participant in ("home", "away"):
                        row["home_score" if participant == "home" else "away_score"] = value
            mapped_row = _normalise(row, self.key)
            if mapped_row:
                mapped.append(mapped_row)
        if rows and not mapped:
            raise ProviderError("SportMonks returned records, but their fixture fields did not match the current mapper; no records archived.")
        return mapped
