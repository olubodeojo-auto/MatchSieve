#!/usr/bin/env python3
"""Collect a Soccerway match and archive a pipeline-ready JSON envelope.

Example:
  python scripts/collect_soccerway.py "https://www.soccerway.com/match/team-a-id/team-b-id/"
  python scripts/run_agent_pipeline.py knowledge-base/source-snapshots/soccerway/<file>.json --market OVER_UNDER_MATCH_GOALS

The collector preserves page snapshots and gaps. It does not bypass access
controls, CAPTCHAs, rate limits or any source restrictions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from matchsieve.collectors.soccerway import SoccerwayAdapter  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect and archive one Soccerway match-page set.")
    parser.add_argument("url", help="Soccerway match/game URL")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "knowledge-base" / "source-snapshots" / "soccerway"),
        help="Archive folder (default: knowledge-base/source-snapshots/soccerway)",
    )
    parser.add_argument("--max-pages", type=int, default=9, help="Maximum pages, including overview (1–9)")
    parser.add_argument("--delay-seconds", type=float, default=0.8, help="Delay between tab requests")
    parser.add_argument("--timeout-ms", type=int, default=25_000, help="Per-navigation/default Playwright timeout")
    parser.add_argument("--headed", action="store_true", help="Show the browser window for local troubleshooting")
    args = parser.parse_args()

    try:
        collection = SoccerwayAdapter(
            max_pages=args.max_pages,
            delay_seconds=args.delay_seconds,
            timeout_ms=args.timeout_ms,
            headless=not args.headed,
        ).collect(args.url)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    except Exception as exc:
        parser.exit(2, f"Collection failed ({type(exc).__name__}): {exc}\\n")

    record = (collection.get("records") or [{}])[0]
    facts = record.get("facts") or {}
    fixture = {
        key: facts[key]
        for key in ("home_team", "away_team", "competition", "kickoff", "status", "venue")
        if facts.get(key) not in (None, "")
    }
    envelope = {
        "fixture": fixture,
        "collection": collection,
        "archive_metadata": {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": "Soccerway",
            "purpose": "prematch research collection; review data licensing and freshness before commercial use",
        },
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(collection.get("source_url", args.url).encode("utf-8")).hexdigest()[:12]
    date_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = out_dir / f"soccerway_{date_tag}_{digest}.json"
    target.write_text(json.dumps(envelope, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    summary = {
        "status": collection.get("status"),
        "archive": str(target),
        "source_url": collection.get("source_url"),
        "pages_captured": len(collection.get("pages") or []),
        "record_count": collection.get("records_collected", 0),
        "fixture_fields_found": sorted(fixture),
        "missing_fields": (record.get("raw_payload") or {}).get("missing_fields", []),
        "warnings": collection.get("warnings", []),
        "errors": collection.get("errors", []),
        "next_step": "Review the archived fields and source permissions before running the specialist pipeline or using the data commercially.",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if collection.get("status") in {"success", "partial"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
