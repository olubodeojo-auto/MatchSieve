from __future__ import annotations

import os
from typing import Any

from .base import ProviderError
from .http_json import get_json


class TheSportsDBProvider:
    """Supplementary schedule adapter using TheSportsDB's free v1 API."""

    key = "thesportsdb"
    base_url = "https://www.thesportsdb.com/api/v1/json"

    def fetch_fixtures(self, date: str, sport: str = "Soccer", league: str | None = None) -> list[dict[str, Any]]:
        # TheSportsDB documents 123 as its shared free v1 key. A private premium key
        # may be supplied through THESPORTSDB_API_KEY without changing code.
        token = os.getenv("THESPORTSDB_API_KEY", "123").strip() or "123"
        payload = get_json(f"{self.base_url}/{token}/eventsday.php", params={"d": date, "s": sport})
        if not isinstance(payload, dict):
            raise ProviderError("TheSportsDB returned an unexpected response type.")
        rows = payload.get("events")
        if rows is None:
            return []
        if not isinstance(rows, list):
            raise ProviderError("TheSportsDB response did not contain an events list.")
        out: list[dict[str, Any]] = []
        for item in rows:
            if not isinstance(item, dict):
                continue
            event_sport = str(item.get("strSport") or "").strip().lower()
            if sport and event_sport and event_sport != sport.strip().lower():
                continue
            comp = item.get("strLeague") or "Unknown competition"
            if league and league.strip().lower() not in str(comp).lower():
                continue
            home, away = item.get("strHomeTeam"), item.get("strAwayTeam")
            day, time = item.get("dateEvent"), item.get("strTime")
            if not home or not away or not day:
                continue
            # The API's event time may be local/unspecified. Keep date-only values
            # as date-only instead of falsely labelling them UTC.
            kickoff = f"{day}T{time}" if time and time not in {"00:00:00", "00:00"} else day
            row: dict[str, Any] = {
                "external_id": item.get("idEvent"),
                "competition": comp,
                "season": item.get("strSeason"),
                "kickoff_utc": kickoff,
                "home_team": home,
                "away_team": away,
                "status": "finished" if item.get("intHomeScore") not in (None, "") and item.get("intAwayScore") not in (None, "") else "scheduled",
                "source_key": self.key,
                "source_url": "https://www.thesportsdb.com/",
                "quality_label": "source-reported-timezone-unverified",
                "provider_payload": item,
            }
            hs, aw = item.get("intHomeScore"), item.get("intAwayScore")
            if hs not in (None, "") and aw not in (None, ""):
                try:
                    row["home_score"], row["away_score"] = int(hs), int(aw)
                except (ValueError, TypeError):
                    row["status"] = "scheduled"
            out.append(row)
        return out
