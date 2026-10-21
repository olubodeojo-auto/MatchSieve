import argparse
import json
from datetime import datetime, timezone
from matchsieve.provider_manager import ProviderManager
from matchsieve.repository import Repository

def main():
    today = datetime.now(timezone.utc).date().isoformat()
    p = argparse.ArgumentParser(description="Fetch and archive live football fixtures")
    p.add_argument("--provider", required=True, choices=["api_football", "thesportsdb", "sportscore", "openligadb", "football_data_org"])
    p.add_argument("--date", default=today)
    p.add_argument("--league")
    p.add_argument("--season")
    p.add_argument("--competition")
    p.add_argument("--status")
    a = p.parse_args()
    if a.provider == "api_football":
        kw = {"date": a.date, "league": a.league, "season": a.season, "status": a.status}
    elif a.provider == "thesportsdb":
        kw = {"date": a.date, "sport": "Soccer", "league": a.competition}
    elif a.provider == "sportscore":
        kw = {"date": a.date, "status": a.status or "upcoming", "competition": a.competition}
    elif a.provider == "openligadb":
        if not a.league or not a.season:
            p.error("openligadb requires --league and --season")
        kw = {"league": a.league, "season": a.season}
    else:
        kw = {"date_from": a.date, "date_to": a.date, "competition": a.competition or a.league}
    result = ProviderManager(Repository()).fetch(a.provider, **kw)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    if result.get("status") != "success":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
