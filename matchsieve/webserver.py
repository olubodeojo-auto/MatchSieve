from __future__ import annotations

import json
import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .analytics import MARKETS
from .config import HOST, OLLAMA_ENABLED, OLLAMA_MODEL, PORT, ROOT
from .db import table_counts
from .importers import import_csv
from .provider_manager import ProviderManager
from .reporting import generate_report
from .repository import Repository

WEB = ROOT / "web"
WEB_ASSETS = {"index.html", "app.js", "style.css", "funnel-preview.html"}
MARKET_ORDER = ["UNDER_4_5", "OVER_2_5", "BTTS", "UNDER_3_5", "DOUBLE_CHANCE", "RESULT_1X2", "RESEARCH_BRIEF"]


def mobile_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    return {key: fixture.get(key) for key in (
        "id", "competition", "season", "kickoff_utc", "home_team", "away_team",
        "status", "home_score", "away_score", "source_primary", "source_ref", "venue",
    )}


def mobile_report_from_evidence(report_id: int, evidence: dict[str, Any], markdown: str = "", path: str | None = None,
                                llm_used: bool = False, market_code: str | None = None) -> dict[str, Any]:
    fixture = evidence.get("fixture") or {}
    code = market_code or evidence.get("market_code") or "RESEARCH_BRIEF"
    market = evidence.get("market") or MARKETS.get(code, MARKETS["RESEARCH_BRIEF"])
    limited = evidence.get("status", "LIMITED_EVIDENCE") != "READY_FOR_REVIEW"
    supporting = [{"label": "Supporting signal", "detail": text, "direction": "support"}
                  for text in evidence.get("supporting_signals", [])]
    counter = [{"label": "Counter-signal", "detail": text, "direction": "counter"}
               for text in evidence.get("counter_signals", [])]
    return {
        "id": int(report_id),
        "report_id": int(report_id),
        "fixture": mobile_fixture(fixture),
        "market_code": code,
        "market_label": market.get("label", code),
        "status": evidence.get("status", "LIMITED_EVIDENCE"),
        "summary": (
            "The stored sample is available for a first review. Current team news, line-ups and market context still need verification."
            if not limited else
            "Evidence is incomplete in the current archive. Treat this as a limited research brief, not a prediction or a recommendation."
        ),
        "supporting_evidence": supporting,
        "counter_evidence": counter,
        "missing_data": list(evidence.get("missing_information", [])),
        "source_records": list(evidence.get("sources", [])),
        "h2h": list(evidence.get("h2h", [])),
        "home_form": evidence.get("home_form", {}),
        "away_form": evidence.get("away_form", {}),
        "generated_at_utc": evidence.get("generated_at"),
        "markdown": markdown,
        "path": path,
        "llm_used": bool(llm_used),
        "method_note": evidence.get("method_note", "Figures describe only records stored in the archive; they are not probabilities."),
    }


def mobile_report_from_record(record: dict[str, Any]) -> dict[str, Any]:
    evidence = record.get("report") or {}
    evidence.setdefault("market_code", record.get("market_code"))
    evidence.setdefault("status", record.get("evidence_status"))
    evidence.setdefault("generated_at", record.get("created_at"))
    # If a record's decoded evidence is corrupt/incomplete, preserve the history card without inventing content.
    if not evidence.get("fixture"):
        evidence["fixture"] = {key: record.get(key) for key in (
            "id", "competition", "kickoff_utc", "home_team", "away_team", "fixture_status", "home_score", "away_score", "source_primary", "source_ref"
        )}
        evidence["fixture"]["id"] = record.get("fixture_id")
        evidence["fixture"]["status"] = record.get("fixture_status")
    return mobile_report_from_evidence(
        int(record.get("id", 0)), evidence, str(record.get("markdown") or ""),
        llm_used=bool(record.get("llm_used")), market_code=str(record.get("market_code") or "RESEARCH_BRIEF"),
    )


class Handler(BaseHTTPRequestHandler):
    repo: Repository
    server_version = "MatchSieve/0.3"

    def log_message(self, fmt: str, *args: Any) -> None:
        print("[matchsieve-api] " + fmt % args)

    def _send(self, code: int, body: Any, ctype: str = "application/json; charset=utf-8") -> None:
        if isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("Invalid Content-Length header") from exc
        if length < 0:
            raise ValueError("Invalid request length")
        if length > 1_000_000:
            raise ValueError("Request body too large (1 MB limit)")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        body = json.loads(raw or "{}")
        if not isinstance(body, dict):
            raise ValueError("Request JSON must be an object")
        return body

    @staticmethod
    def _limit(query: dict[str, list[str]], default: int, ceiling: int) -> int:
        try:
            value = int(query.get("limit", [str(default)])[0])
        except (ValueError, TypeError):
            value = default
        return max(1, min(value, ceiling))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        path = parsed.path.rstrip("/") or "/"
        try:
            if path in ("/api/health", "/api/status"):
                counts = table_counts(self.repo.db_path)
                payload = {
                    "ok": True,
                    "product": "MatchSieve",
                    "version": "0.3.0",
                    "counts": counts,
                    "ollama_enabled": OLLAMA_ENABLED,
                    "ollama_model": OLLAMA_MODEL if OLLAMA_ENABLED else None,
                    "markets": MARKETS,
                    "api_contract": "0.2",
                    "production_ready": False,
                    "readiness_note": "Local foundation: authentication, billing, public hosting and live provider validation are not yet complete.",
                }
                self._send(200, payload)
                return
            if path in ("/api/fixtures", "/api/mobile/fixtures"):
                rows = self.repo.list_fixtures(query.get("q", [""])[0], self._limit(query, 100, 250))
                self._send(200, [mobile_fixture(row) for row in rows])
                return
            if path in ("/api/markets", "/api/mobile/markets"):
                self._send(200, [{"code": code, "label": MARKETS[code]["label"], "question": MARKETS[code]["question"], "metric": MARKETS[code]["metric"]} for code in MARKET_ORDER])
                return
            if path in ("/api/research/history", "/api/mobile/research/history"):
                records = self.repo.list_reports(self._limit(query, 20, 100))
                self._send(200, [mobile_report_from_record(row) for row in records])
                return
            if path.startswith("/api/research/") or path.startswith("/api/mobile/research/"):
                try:
                    report_id = int(path.rsplit("/", 1)[1])
                except (ValueError, IndexError):
                    self._send(400, {"error": "Report ID must be a positive integer."})
                    return
                record = self.repo.get_report(report_id)
                if not record:
                    self._send(404, {"error": "Research report not found."})
                    return
                self._send(200, mobile_report_from_record(record))
                return
            if path == "/api/providers":
                self._send(200, ProviderManager(self.repo).catalog())
                return
            if path == "/api/kb-search":
                q = query.get("q", [""])[0].strip()
                self._send(200, self.repo.search_knowledge(q, self._limit(query, 10, 50)))
                return
            asset = "index.html" if path == "/" else path.lstrip("/")
            if asset not in WEB_ASSETS:
                self._send(404, {"error": "Not found"})
                return
            file_path = WEB / asset
            if not file_path.is_file():
                self._send(404, {"error": f"Web asset missing: {asset}"})
                return
            content_type = mimetypes.guess_type(str(file_path))[0] or "text/plain"
            if content_type.startswith("text/") or content_type in ("application/javascript",):
                content_type += "; charset=utf-8"
            self._send(200, file_path.read_text(encoding="utf-8"), content_type)
        except Exception as exc:  # do not crash the whole server on one request
            print(f"[matchsieve-api] GET {path} failed: {type(exc).__name__}: {exc}")
            self._send(500, {"error": "The server could not complete this request. Check the local logs."})

    def do_POST(self) -> None:  # noqa: N802
        path = urllib.parse.urlparse(self.path).path.rstrip("/") or "/"
        try:
            body = self._body()
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send(400, {"error": str(exc) or "Invalid JSON body."})
            return
        try:
            if path == "/api/paste-import":
                from .paste_importer import parse_match_history_paste
                home = str(body.get("home_team") or "").strip()
                away = str(body.get("away_team") or "").strip()
                competition = str(body.get("competition") or "").strip()
                kickoff = str(body.get("kickoff") or "").strip()
                source_url = str(body.get("source_url") or "").strip() or None
                source_name = str(body.get("source_name") or "manual clipboard paste").strip()
                if not home or not away or not competition or not kickoff:
                    raise ValueError("Home team, away team, competition and fixture date/time are required.")
                if home.casefold() == away.casefold():
                    raise ValueError("Home and away teams must be different.")
                parsed = parse_match_history_paste(
                    str(body.get("text") or ""), source_name=source_name,
                    home_team=home, away_team=away,
                )
                if not parsed["total_records"]:
                    self._send(422, {"error": "No match-history rows were recognised. Keep the three section headings and use one match per line with date, competition, teams and score.", "preview": parsed})
                    return
                source_key = "manual_match_history_paste"
                fixture_payload = {
                    "home_team": home, "away_team": away, "competition": competition,
                    "kickoff_utc": kickoff, "status": "scheduled", "source_key": source_key,
                    "source_ref": "paste:" + parsed["source_sha256"][:16],
                    "source_url": source_url, "pasted_match_history": parsed,
                }
                fixture_id = self.repo.add_fixture(
                    fixture_payload, source_key=source_key,
                    source_ref=fixture_payload["source_ref"], source_url=source_url,
                    raw_payload={"fixture": {k: v for k, v in fixture_payload.items() if k != "pasted_match_history"}, "history": parsed},
                )
                imported = 0
                import_errors = []
                for section_name, rows in parsed["sections"].items():
                    for index, row in enumerate(rows, start=1):
                        try:
                            history_item = {
                                "home_team": row["home_team"], "away_team": row["away_team"],
                                "competition": row["competition"], "kickoff_utc": row["date"] + "T12:00:00Z",
                                "home_score": row["home_score"], "away_score": row["away_score"],
                                "status": "finished", "source_key": source_key,
                                "source_ref": f"{parsed['source_sha256'][:16]}:{section_name}:{index}",
                                "history_section": section_name,
                                "history_venue_context": row["venue_context"],
                            }
                            self.repo.add_fixture(
                                history_item, source_key=source_key,
                                source_ref=history_item["source_ref"], source_url=source_url,
                                raw_payload={"section": section_name, "record": row, "paste_sha256": parsed["source_sha256"]},
                            )
                            imported += 1
                        except (TypeError, ValueError, KeyError) as exc:
                            import_errors.append(f"{section_name} record {index}: {exc}")
                result = {
                    "fixture_id": fixture_id, "fixture": mobile_fixture(self.repo.get_fixture(fixture_id) or {}),
                    "status": "partial" if parsed["errors"] or import_errors else "success",
                    "sections": parsed["coverage"], "records_parsed": parsed["total_records"],
                    "historical_records_archived": imported, "warnings": parsed["errors"] + import_errors,
                    "ignored_noise_lines": parsed["ignored_noise_lines"],
                    "excluded_fields": parsed["excluded_fields"],
                }
                self._send(201, result)
                return
            if path == "/api/fixture":
                fixture_id = self.repo.add_fixture(
                    body, source_key=body.get("source_key", "manual"),
                    source_ref=body.get("source_ref", "entered in MatchSieve local workspace"),
                    source_url=body.get("source_url"), raw_payload=body,
                )
                kb_index = {}
                try:
                    from .kb_writer import refresh_indexes
                    kb_index = refresh_indexes(self.repo)
                except Exception as exc:
                    kb_index = {"warning": str(exc)}
                self._send(201, {"fixture_id": fixture_id, "fixture": mobile_fixture(self.repo.get_fixture(fixture_id) or {}), "knowledge_base": kb_index})
                return
            if path in ("/api/research", "/api/mobile/research"):
                fixture_id = body.get("fixture_id")
                market_code = str(body.get("market") or body.get("market_code") or "RESEARCH_BRIEF")
                if fixture_id is None:
                    raise ValueError("fixture_id is required")
                try:
                    fixture_id = int(fixture_id)
                except (ValueError, TypeError) as exc:
                    raise ValueError("fixture_id must be an integer") from exc
                # AI commentary remains opt-in and only runs if locally configured.
                use_ollama = bool(body.get("ollama", body.get("include_commentary", False)))
                result = generate_report(fixture_id, market_code, self.repo, use_ollama)
                if path == "/api/mobile/research":
                    self._send(200, mobile_report_from_evidence(result["report_id"], result["report"], result["markdown"], result["path"], result["llm_used"], market_code))
                else:
                    self._send(200, {key: result[key] for key in ("report_id", "path", "status", "llm_used", "report", "markdown")})
                return
            if path == "/api/provider-fetch":
                provider = str(body.get("provider") or "").strip().lower()
                if not provider:
                    raise ValueError("provider is required")
                kwargs: dict[str, Any] = {}
                if provider == "sportscore":
                    from datetime import datetime, timezone
                    kwargs = {
                        "date": str(body.get("date") or datetime.now(timezone.utc).date().isoformat()),
                        "status": str(body.get("status") or "upcoming"),
                        "competition": str(body.get("competition") or "").strip() or None,
                    }
                elif provider == "football_data_org":
                    from datetime import datetime, timezone
                    today = datetime.now(timezone.utc).date().isoformat()
                    kwargs = {
                        "date_from": str(body.get("date_from") or body.get("date") or today),
                        "date_to": str(body.get("date_to") or body.get("date") or today),
                        "competition": str(body.get("competition") or "").strip() or None,
                    }
                elif provider == "openligadb":
                    kwargs = {"league": str(body.get("league") or "").strip(), "season": str(body.get("season") or "").strip()}
                result = ProviderManager(self.repo).fetch(provider, **kwargs)
                status_code = 200 if result.get("status") == "success" else 409
                self._send(status_code, result)
                return
            if path == "/api/import-csv":
                name = Path(str(body.get("filename", ""))).name
                inbox = (ROOT / "data" / "inbox").resolve()
                file_path = (inbox / name).resolve()
                if file_path.parent != inbox or not file_path.is_file():
                    raise ValueError("Put the CSV file inside data/inbox, then enter its filename.")
                result = import_csv(file_path, self.repo, str(body.get("source_key", "manual_csv")), body.get("source_url"))
                self._send(200, result)
                return
            self._send(404, {"error": "Not found"})
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
        except Exception as exc:
            print(f"[matchsieve-api] POST {path} failed: {type(exc).__name__}: {exc}")
            self._send(500, {"error": "The server could not complete this request. Check the local logs."})


def serve(host: str = HOST, port: int = PORT, repo: Repository | None = None) -> None:
    Handler.repo = repo or Repository()
    server = ThreadingHTTPServer((host, int(port)), Handler)
    print(f"MatchSieve running at http://{host}:{port}")
    print("LOCAL FOUNDATION ONLY. Keep host at 127.0.0.1 except for deliberate, trusted LAN development.")
    print("Public deployment requires authentication, rate limits, TLS, billing entitlements and operational monitoring.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nStopping MatchSieve...")
    finally:
        server.server_close()
