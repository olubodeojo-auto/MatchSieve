from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Direct execution adds scripts/ to sys.path, so add the repository root too.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from matchsieve.provider_manager import ProviderManager
from matchsieve.repository import Repository

def main() -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    parser = argparse.ArgumentParser(description="Fetch and archive live football fixtures")
    parser.add_argument("--provider", required=True, choices=[
        "api_football", "thesportsdb", "sportscore", "openligadb", "football_data_org"
    ])
    parser.add_argument("--date", default=today)
    parser.add_argument("--league")
    parser.add_argument("--season")
    parser.add_argument("--competition")
    parser.add_argument("--status")
    args = parser.parse_args()

    if args.provider == "api_football":
        kwargs = {"date": args.date, "league": args.league, "season": args.season, "status": args.status}
    elif args.provider == "thesportsdb":
        kwargs = {"date": args.date, "sport": "Soccer", "league": args.competition}
    elif args.provider == "sportscore":
        kwargs = {"date": args.date, "status": args.status or "upcoming", "competition": args.competition}
    elif args.provider == "openligadb":
        if not args.league or not args.season:
            parser.error("openligadb requires --league and --season")
        kwargs = {"league": args.league, "season": args.season}
    else:
        kwargs = {"date_from": args.date, "date_to": args.date, "competition": args.competition or args.league}

    result = ProviderManager(Repository()).fetch(args.provider, **kwargs)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    if result.get("status") != "success":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
