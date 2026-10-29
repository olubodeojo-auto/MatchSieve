#!/usr/bin/env python3
"""Smoke-test the installed local model using explicitly synthetic, non-match evidence.

This script intentionally bypasses the MatchSieve research pipeline and produces no
football report or betting recommendation. It only checks the local Ollama connection,
JSON response shape, and evidence-ID citation handling.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from matchsieve.agents.local_llm import LocalLLMError, LocalOllamaClient


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    research = {
        "fixture": {"home_team": "Synthetic Home FC", "away_team": "Synthetic Away FC"},
        "market": "SMOKE_TEST_ONLY",
        "evidence_gaps": ["Synthetic smoke test; this is not a real match or current football evidence."],
    }
    evidence = [{
        "record_id": "local-llm-smoke-test-1",
        "source": "synthetic_local_llm_smoke_test",
        "captured_at": now,
        "facts": {
            "home_team": "Synthetic Home FC",
            "away_team": "Synthetic Away FC",
            "competition": "SMOKE TEST — NOT A REAL COMPETITION",
            "kickoff": "NOT APPLICABLE",
        },
        "raw_payload": {
            "test_only": True,
            "supporting_signals": [
                "SYNTHETIC TEST FACT: Home side won 3 of 5 fictional sample matches."
            ],
            "against_signals": [
                "SYNTHETIC TEST FACT: Away side won 4 of 5 fictional sample matches."
            ],
            "notes": ["These invented values exist only to test the local model connection."],
        },
    }]

    try:
        result = LocalOllamaClient().analyse(research, evidence)
    except LocalLLMError as exc:
        print(f"Local LLM smoke test failed: {exc}")
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") != "llm_analysis_complete":
        print("The local API responded, but analysis needs review; inspect the result above.")
        return 1
    print("Local model response and required JSON fields verified. Smoke-test data is synthetic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
