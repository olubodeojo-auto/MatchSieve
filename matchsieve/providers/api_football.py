from __future__ import annotations

import os
from typing import Any

from .base import ProviderError
from .http_json import get_json


class ApiFootballProvider:
    """Live fixtures adapter for API-Football v3 (API-Sports)."""

    key = "api_football"
    base_url = "https://v3.football.api-sports.io"

    def fetch_fixtures(self, date: str, league: int | str | None = None,
                       season: int | str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        token = os.getenv("API_FOOTBALL_KEY", "").strip()
        if not token:
            raise ProviderError("Set API_FOOTBALL_KEY in local .env before using API-Football.")
        params: dict[str, Any] = {"date": date, "timezone": "UTC"}
        if league not in (None, ""):
            params["league"] = league
        if season not in (None, ""):
            params["season"] = season
        if status not in (None, ""):
            params["status"] = status
        payload = get_json(
            f"{self.base_url}/fixtures",
            params=params,
            headers={"x-apisports-key": token},
        )
        if not isinstance(payload, dict):
            raise ProviderError("API-Football returned an unexpected response type.")
        if payload.get("errors"):
            raise ProviderError(f"API-Football rejected the request: {str(payload['errors'])[:300]}")
        rows = payload.get("response")
        if not isinstance(rows, list):
            raise ProviderError("API-Football response did not contain a fixtures list.")
        out: list[dict[str, Any]] = []
        for item in rows:
            if not isinstance(item, dict):
                continue
            fixture = item.get("fixture") or {}
            teams = item.get("teams") or {}
            home = teams.get("home") or {}
            away = teams.get("away") or {}
            league_data = item.get("league") or {}
            goals = item.get("goals") or {}
            kickoff = fixture.get("date")
            if not home.get("name") or not away.get("name") or not kickoff:
                continue
            status_data = fixture.get("status") or {}
            short_status = str(status_data.get("short") or "").upper()
            score_home, score_away = goals.get("home"), goals.get("away")
            finished = short_status in {"FT", "AET", "PEN"}
            row: dict[str, Any] = {
                "external_id": fixture.get("id"),
                "competition": league_data.get("name") or "Unknown competition",
                "season": league_data.get("season"),
                "kickoff_utc": kickoff,
                "home_team": home["name"],
                "away_team": away["name"],
                "status": "finished" if finished else (str(status_data.get("long") or "scheduled").lower()),
                "source_key": self.key,
                "source_url": "https://www.api-football.com/",
                "quality_label": "source-reported-unreviewed",
                "provider_payload": item,
            }
            if score_home is not None and score_away is not None:
                row["home_score"], row["away_score"] = int(score_home), int(score_away)
            halftime = (item.get("score") or {}).get("halftime") or {}
            if halftime.get("home") is not None:
                row["halftime_home_score"] = int(halftime["home"])
            if halftime.get("away") is not None:
                row["halftime_away_score"] = int(halftime["away"])
            out.append(row)
        return out
