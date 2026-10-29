#!/usr/bin/env python3
"""Run MatchSieve's evidence pipeline on saved JSON, optionally using local Ollama.

The standard run is offline. With --local-llm, the script calls only the local
Ollama HTTP service at 127.0.0.1 by default; no hosted AI API is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from matchsieve.agents import MatchSieveAgentPipeline
from matchsieve.agents.local_llm import LocalOllamaClient


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run MatchSieve specialist agents on collected football evidence."
    )
    parser.add_argument("input_json", help="JSON file containing fixture and collection objects")
    parser.add_argument("--market", required=True, choices=[
        "RESULT_1X2", "DOUBLE_CHANCE", "DRAW_NO_BET",
        "OVER_UNDER_MATCH_GOALS", "OVER_UNDER_TEAM_GOALS",
    ])
    parser.add_argument("--advice-requested", action="store_true")
    parser.add_argument("--output", default="data/agent-report.json")
    parser.add_argument(
        "--local-llm", action="store_true",
        help="Use an installed local Ollama model for evidence interpretation.",
    )
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--ollama-model", default="qwen2.5:7b")
    args = parser.parse_args()

    source = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    if (
        not isinstance(source, dict)
        or not isinstance(source.get("fixture"), dict)
        or not isinstance(source.get("collection"), dict)
    ):
        parser.error("Input must be an object with fixture and collection objects.")

    llm_client = (
        LocalOllamaClient(base_url=args.ollama_url, model=args.ollama_model)
        if args.local_llm else None
    )
    result = MatchSieveAgentPipeline(llm_client=llm_client).run(
        source["collection"], source["fixture"], args.market, args.advice_requested
    )
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path = target.with_suffix(".md")
    markdown_path.write_text(result["report"]["markdown"], encoding="utf-8")

    llm = result.get("llm_analysis")
    if llm is not None:
        llm_path = target.with_name(target.stem + ".llm.json")
        llm_path.write_text(json.dumps(llm, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print(json.dumps({
        "pipeline_status": result["pipeline_status"],
        "output": str(target),
        "report_markdown": str(markdown_path),
        "records_collected": result["collection"].get("records_collected", len(result["collection"].get("records", []))),
        "quality": result["quality"].get("overall_status"),
        "recommendation_status": result["report"].get("recommendation_status"),
        "local_llm_enabled": args.local_llm,
        "local_llm_status": llm.get("status") if llm else "disabled",
        "publication_allowed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
