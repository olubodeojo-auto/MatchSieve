from __future__ import annotations
from typing import Any
import os
from .http_json import get_json
from .base import ProviderError

class SportScoreProvider:
    key="sportscore"
    base_url="https://sportscore.com/api/v1/fixtures/"

    def fetch_fixtures(self, date: str, status: str="upcoming", competition: str | None=None, limit: int=200) -> list[dict[str,Any]]:
        """Fetch one UTC calendar date. This adapter is unverified until a live smoke test succeeds."""
        token = os.getenv("SPORTSCORE_API_KEY", "").strip()
        headers = {"X-Api-Key": token} if token else {}
        payload=get_json(self.base_url,params={"sport":"football","date":date,"status":status,"competition":competition,"limit":min(200,limit)},headers=headers)
        rows=_extract_rows(payload)
        return [_normalise(x) for x in rows if isinstance(x,dict)]


def _extract_rows(payload: Any) -> list[dict[str,Any]]:
    if isinstance(payload,list): return payload
    if isinstance(payload,dict):
        for key in ("data","fixtures","matches","results"):
            if isinstance(payload.get(key),list): return payload[key]
    raise ProviderError("SportScore response did not contain a recognised fixture list; save a redacted sample for adapter mapping")


def _normalise(x: dict[str,Any]) -> dict[str,Any]:
    home=x.get("home_team") or x.get("homeTeam") or x.get("home") or x.get("team_home") or {}
    away=x.get("away_team") or x.get("awayTeam") or x.get("away") or x.get("team_away") or {}
    def team(t): return t.get("name") or t.get("title") or t.get("team_name") if isinstance(t,dict) else t
    kickoff=x.get("kickoff_utc") or x.get("start_time") or x.get("startTime") or x.get("date") or x.get("match_date")
    comp=x.get("competition") or x.get("league") or {}
    comp=comp.get("name") or comp.get("title") or comp.get("slug") if isinstance(comp,dict) else comp
    if not team(home) or not team(away) or not kickoff:
        raise ProviderError("SportScore fixture omitted team or kickoff field; mapping needs review")
    result={"external_id":x.get("id") or x.get("match_id") or x.get("slug"),"competition":comp or "Unknown competition",
            "kickoff_utc":kickoff,"home_team":str(team(home)),"away_team":str(team(away)),"status":x.get("status") or "scheduled",
            "source_key":"sportscore","source_url":"https://sportscore.com/developers/api/","quality_label":"unreviewed"}
    hs=x.get("home_score",x.get("homeScore")); as_=x.get("away_score",x.get("awayScore"))
    if isinstance(x.get("score"),dict):
        hs=x['score'].get('home',hs); as_=x['score'].get('away',as_)
    if hs is not None and as_ is not None:
        try: result.update(home_score=int(hs),away_score=int(as_),status="finished")
        except (ValueError,TypeError): pass
    # Preserve raw values outside core fields to support later remapping.
    result['provider_payload']=x
    return result
