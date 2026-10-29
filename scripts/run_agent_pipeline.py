#!/usr/bin/env python3
"""Run MatchSieve's evidence pipeline on saved JSON, optionally using local Ollama.

The standard run is offline. With --local-llm, the script calls only the local
Ollama HTTP service at 127.0.0.1 by default; no hosted AI API is used.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from matchsieve.agents import MatchSieveAgentPipeline
from matchsieve.agents.local_llm import LocalLLMError, LocalOllamaClient


def render_local_llm_markdown(result: dict) -> str:
    """Render the separate LLM analysis with its evidence IDs and review warnings."""
    analysis = result.get("analysis")
    lines = [
        "# MatchSieve Local LLM Analysis",
        "",
        f"**Validation status:** {result.get('status', 'unknown')}",
        f"**Model:** {result.get('model', 'not recorded')}",
        "**Publication:** Disabled — human review required.",
        "",
        "> Evidence-ID checks establish traceability, not that a claim is correct. Check each cited source.",
    ]
    if not isinstance(analysis, dict):
        lines.extend(["", "## Result", "", str(result.get("error", "No analysis was returned."))])
        return "\n".join(lines) + "\n"

    flagged = {item.get("claim") for item in result.get("unsupported_claims", [])}
    lines.extend(["", "## Summary", "", str(analysis.get("summary", "No summary returned."))])
    for section, title in (
        ("supporting_points", "Supporting points"),
        ("counter_points", "Counter-evidence"),
    ):
        lines.extend(["", f"## {title}", ""])
        points = analysis.get(section) or []
        if not points:
            lines.append("- No point was supplied.")
        for point in points:
            claim = str(point.get("claim", "Invalid point"))
            ids = point.get("evidence_record_ids") or []
            marker = "REVIEW REQUIRED — citation missing/invalid" if claim in flagged else "Traceable ID(s)"
            lines.append(f"- **{marker}:** {claim} _(records: {', '.join(map(str, ids)) or 'none'})_")
    lines.extend(["", "## Data quality concerns", ""])
    lines.extend([f"- {item}" for item in (analysis.get("data_quality_concerns") or [])] or ["- None reported by the model."])
    lines.extend(["", "## Market assessment", "", str(analysis.get("market_assessment", "No market assessment returned."))])
    lines.extend(["", "## Limitations", ""])
    lines.extend([f"- {item}" for item in (analysis.get("limitations") or [])] or ["- No limitations supplied by the model."])
    lines.extend(["", "## Final gate", "", f"**Model decision:** {analysis.get('decision', 'INSUFFICIENT_EVIDENCE')}", "**Publication allowed:** No"])
    return "\n".join(lines) + "\n"


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
    parser.add_argument("--ollama-model", default=os.environ.get("MATCHSIEVE_OLLAMA_MODEL", "qwen2.5:7b"))
    args = parser.parse_args()

    source = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    if (
        not isinstance(source, dict)
        or not isinstance(source.get("fixture"), dict)
        or not isinstance(source.get("collection"), dict)
    ):
        parser.error("Input must be an object with fixture and collection objects.")

    try:
        llm_client = (
            LocalOllamaClient(base_url=args.ollama_url, model=args.ollama_model)
            if args.local_llm else None
        )
        result = MatchSieveAgentPipeline(llm_client=llm_client).run(
            source["collection"], source["fixture"], args.market, args.advice_requested
        )
    except LocalLLMError as exc:
        parser.error(str(exc))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path = target.with_suffix(".md")
    markdown_path.write_text(result["report"]["markdown"], encoding="utf-8")

    llm = result.get("llm_analysis")
    llm_markdown_path = None
    if llm is not None:
        llm_path = target.with_name(target.stem + ".llm.json")
        llm_path.write_text(json.dumps(llm, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        llm_markdown_path = target.with_name(target.stem + ".llm.md")
        llm_markdown_path.write_text(render_local_llm_markdown(llm), encoding="utf-8")

    print(json.dumps({
        "pipeline_status": result["pipeline_status"],
        "output": str(target),
        "report_markdown": str(markdown_path),
        "records_collected": result["collection"].get("records_collected", len(result["collection"].get("records", []))),
        "quality": result["quality"].get("overall_status"),
        "recommendation_status": result["report"].get("recommendation_status"),
        "local_llm_enabled": args.local_llm,
        "local_llm_status": llm.get("status") if llm else "disabled",
        "local_llm_markdown": str(llm_markdown_path) if llm_markdown_path else None,
        "publication_allowed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
