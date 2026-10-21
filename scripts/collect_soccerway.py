#!/usr/bin/env python3
"""Collect a Soccerway date fixture list or one selected match into the local archive.

Examples:
  python scripts/collect_soccerway.py --date-url "https://ng.soccerway.com/"
  python scripts/collect_soccerway.py --date-url "https://ng.soccerway.com/matches/?date=2026-10-21"
  python scripts/collect_soccerway.py --match-url "https://ng.soccerway.com/match/como-ttyLthOA/manchester-united-ppjDR086/"
  python scripts/collect_soccerway.py --date-url "https://ng.soccerway.com/" --save-fixtures

The script archives source snapshots locally, never bypasses access controls, and
does not claim commercial rights to source data.
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


def archive_payload(output_dir: Path, source: str, payload: dict) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    date_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = output_dir / f"soccerway_{date_tag}_{digest}.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect a Soccerway date's fixtures or one selected match.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--date-url", help="Soccerway match list/day page URL")
    group.add_argument("--match-url", help="One Soccerway match/game URL")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "knowledge-base" / "source-snapshots" / "soccerway"),
        help="Archive directory for dated JSON records",
    )
    parser.add_argument("--max-fixtures", type=int, default=500, help="Maximum visible fixture links to store (default 500)")
    parser.add_argument("--max-pages", type=int, default=16, help="Maximum detail pages to visit, including overview/H2H")
    parser.add_argument("--delay-seconds", type=float, default=0.8, help="Delay between match tabs")
    parser.add_argument("--timeout-ms", type=int, default=25_000, help="Per-navigation/default Playwright timeout")
    parser.add_argument("--headed", action="store_true", help="Show the browser for local selector review")
    parser.add_argument("--save-fixtures", action="store_true", help="For --date-url, archive the extracted fixture list")
    parser.add_argument("--match-index", type=int, help="Optional 1-based fixture number from a supplied date URL; use after reviewing the saved list")
    args = parser.parse_args()

    adapter = SoccerwayAdapter(
        max_pages=args.max_pages,
        delay_seconds=args.delay_seconds,
        timeout_ms=args.timeout_ms,
        headless=not args.headed,
    )
    output_dir = Path(args.output_dir)
    try:
        if args.date_url:
            result = adapter.collect_fixtures_for_date(args.date_url, max_fixtures=args.max_fixtures)
            archive_path = None
            if args.save_fixtures or result.get("status") in {"success", "partial"}:
                archive_path = archive_payload(output_dir, result.get("source_url", args.date_url), result)
            fixtures = result.get("fixtures", [])
            selected_index = args.match_index
            if selected_index is not None:
                if selected_index < 1 or selected_index > len(fixtures):
                    parser.error(f"--match-index must be between 1 and {len(fixtures)} for the collected date list.")
                selected = fixtures[selected_index - 1]
                detail = adapter.collect(selected["source_url"])
                detail_path = archive_payload(output_dir, detail.get("source_url", selected["source_url"]), detail)
                print(json.dumps({
                    "status": detail.get("status"),
                    "date_list_archive": str(archive_path) if archive_path else None,
                    "selected_fixture_number": selected_index,
                    "selected_fixture": selected,
                    "detail_archive": str(detail_path),
                    "pages_captured": len(detail.get("pages") or []),
                    "missing_fields": ((detail.get("records") or [{}])[0].get("raw_payload") or {}).get("missing_fields", []),
                    "warnings": detail.get("warnings", []),
                    "errors": detail.get("errors", []),
                    "note": "Fixture-list order is source page order. Review the fixture list first; do not rely on an index if the page/order changed.",
                }, ensure_ascii=False, indent=2))
                return 0 if detail.get("status") in {"success", "partial"} else 2
            print(json.dumps({
                "status": result.get("status"),
                "archive": str(archive_path) if archive_path else None,
                "source_url": result.get("source_url"),
                "fixture_count": len(fixtures),
                "fixtures": [{
                    "index": i + 1,
                    "competition": row.get("competition"),
                    "kickoff": row.get("kickoff_display"),
                    "home_team": row.get("home_team"),
                    "away_team": row.get("away_team"),
                    "score": row.get("score"),
                    "status": row.get("status"),
                    "url": row.get("source_url"),
                } for i, row in enumerate(fixtures)],
                "warnings": result.get("warnings", []),
                "errors": result.get("errors", []),
                "next_step": "Review the list, then collect one selected fixture using --match-url or --match-index.",
            }, ensure_ascii=False, indent=2))
            return 0 if result.get("status") in {"success", "partial"} else 2

        result = adapter.collect(args.match_url)
        archive_path = archive_payload(output_dir, result.get("source_url", args.match_url), result)
        record = (result.get("records") or [{}])[0]
        facts = record.get("facts") or {}
        print(json.dumps({
            "status": result.get("status"),
            "archive": str(archive_path),
            "source_url": result.get("source_url"),
            "pages_captured": len(result.get("pages") or []),
            "record_count": result.get("records_collected", 0),
            "fixture": {key: facts.get(key) for key in ("home_team","away_team","competition","kickoff","status","venue","home_score","away_score") if facts.get(key) is not None},
            "missing_fields": (record.get("raw_payload") or {}).get("missing_fields", []),
            "history_expansion": (record.get("raw_payload") or {}).get("history_expansion", {}),
            "warnings": result.get("warnings", []),
            "errors": result.get("errors", []),
            "next_step": "Review the stored source fields, missing fields and source permissions before research use.",
        }, ensure_ascii=False, indent=2))
        return 0 if result.get("status") in {"success", "partial"} else 2
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    except Exception as exc:
        parser.exit(2, f"Collection failed ({type(exc).__name__}): {exc}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
