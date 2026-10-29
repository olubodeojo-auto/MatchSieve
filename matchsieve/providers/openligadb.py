from __future__ import annotations
from typing import Any
from urllib.parse import quote
from .http_json import get_json
from .base import ProviderError
from ..normalise import parse_datetime

class OpenLigaDBProvider:
    key="openligadb"
    base_url="https://api.openligadb.de"

    def fetch_fixtures(self, league: str, season: str, date_from: str | None=None,
                       date_to: str | None=None) -> list[dict[str,Any]]:
        if not league or not season: raise ValueError("OpenLigaDB requires a league shortcut and season")
        if date_from and date_to and date_from > date_to:
            raise ValueError("date_from must be on or before date_to.")
        payload=get_json(f"{self.base_url}/getmatchdata/{quote(str(league))}/{quote(str(season))}")
        if not isinstance(payload,list): raise ProviderError("OpenLigaDB did not return a match list")
        out=[]
        for x in payload:
            h=x.get('team1') or {}; a=x.get('team2') or {}
            kickoff=x.get('matchDateTimeUTC') or x.get('matchDateTime')
            if not h.get('teamName') or not a.get('teamName') or not kickoff: continue
            match_day=parse_datetime(str(kickoff))[:10]
            if date_from and match_day < date_from: continue
            if date_to and match_day > date_to: continue
            row={"external_id":x.get('matchID'),"competition":x.get('leagueName') or league,"season":season,
                 "kickoff_utc":kickoff,"home_team":h['teamName'],"away_team":a['teamName'],"status":"scheduled",
                 "source_key":"openligadb","source_url":"https://www.openligadb.de/","quality_label":"unreviewed","provider_payload":x}
            result_list=x.get('matchResults') or []
            final=next((r for r in result_list if str(r.get('resultName','')).lower() in ('endresult','endergebnis','final')),None)
            if final and final.get('pointsTeam1') is not None and final.get('pointsTeam2') is not None:
                row.update(home_score=int(final['pointsTeam1']),away_score=int(final['pointsTeam2']),status='finished')
            out.append(row)
        return out
