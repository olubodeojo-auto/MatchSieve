#!/usr/bin/env python3
"""Run the separated MatchSieve agents on a saved collection JSON envelope.

Input JSON shape:
{
  "fixture": {"home_team":"...", "away_team":"...", "competition":"...", "kickoff":"..."},
  "collection": {"records":[{"record_id":"...", "source":"...", "source_url":"https://...",
    "captured_at":"2026-10-21T12:00:00+00:00", "facts":{"home_team":"...", "away_team":"...",
    "competition":"...", "kickoff":"..."}, "raw_payload":{}}]}
}
This runner is deliberately offline: it does not make provider requests or use sample data.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from matchsieve.agents import MatchSieveAgentPipeline

def main() -> int:
    parser = argparse.ArgumentParser(description="Run the MatchSieve specialist-agent pipeline on collected evidence.")
    parser.add_argument("input_json", help="Path to a JSON file containing fixture and collection objects")
    parser.add_argument("--market", required=True, choices=[
        "RESULT_1X2", "DOUBLE_CHANCE", "DRAW_NO_BET", "OVER_UNDER_MATCH_GOALS", "OVER_UNDER_TEAM_GOALS"])
    parser.add_argument("--advice-requested", action="store_true")
    parser.add_argument("--output", default="data/agent-report.json")
    args = parser.parse_args()
    source = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    if not isinstance(source, dict) or not isinstance(source.get("fixture"), dict) or not isinstance(source.get("collection"), dict):
        parser.error("Input must be an object with fixture and collection objects.")
    result = MatchSieveAgentPipeline().run(source["collection"], source["fixture"], args.market, args.advice_requested)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path = target.with_suffix(".md")
    markdown_path.write_text(result["report"]["markdown"], encoding="utf-8")
    print(json.dumps({"pipeline_status":result["pipeline_status"],"output":str(target),"report_markdown":str(markdown_path),
                      "records_collected":result["collection"].get("records_collected"),
                      "quality":result["quality"].get("overall_status"),
                      "recommendation_status":result["report"].get("recommendation_status")}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
