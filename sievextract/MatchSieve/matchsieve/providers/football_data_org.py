from __future__ import annotations
import os
from typing import Any
from .http_json import get_json
from .base import ProviderError

class FootballDataOrgProvider:
    key="football_data_org"
    base_url="https://api.football-data.org/v4"

    def fetch_fixtures(self, date_from: str, date_to: str, competition: str | None=None) -> list[dict[str,Any]]:
        token=os.getenv("FOOTBALL_DATA_ORG_TOKEN","").strip()
        if not token: raise ProviderError("Set FOOTBALL_DATA_ORG_TOKEN in local .env before using Football-Data.org")
        params={"dateFrom":date_from,"dateTo":date_to}
        if competition: params['competitions']=competition
        payload=get_json(f"{self.base_url}/matches",params=params,headers={"X-Auth-Token":token})
        rows=payload.get('matches') if isinstance(payload,dict) else None
        if not isinstance(rows,list): raise ProviderError("Football-Data.org response did not contain matches list")
        out=[]
        for x in rows:
            home=x.get('homeTeam') or {}; away=x.get('awayTeam') or {}; comp=x.get('competition') or {}
            if not home.get('name') or not away.get('name') or not x.get('utcDate'): continue
            item={"external_id":x.get('id'),"competition":comp.get('name') or comp.get('code') or "Unknown competition",
                  "season":str((x.get('season') or {}).get('startDate',''))[:4] or None,"kickoff_utc":x['utcDate'],
                  "home_team":home['name'],"away_team":away['name'],"status":str(x.get('status') or 'scheduled').lower(),
                  "source_key":self.key,"source_url":"https://www.football-data.org/","quality_label":"unreviewed","provider_payload":x}
            score=x.get('score') or {}; full=score.get('fullTime') or {}
            if full.get('home') is not None and full.get('away') is not None:
                item.update(home_score=int(full['home']),away_score=int(full['away']),status='finished')
            half=score.get('halfTime') or {}
            if half.get('home') is not None: item['halftime_home_score']=int(half['home'])
            if half.get('away') is not None: item['halftime_away_score']=int(half['away'])
            out.append(item)
        return out
