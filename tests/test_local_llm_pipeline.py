from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Any

from matchsieve.agents.pipeline import MatchSieveAgentPipeline


class FakeLLM:
    def __init__(self, response: dict[str, Any]):
        self.response = response
        self.received_evidence = None

    def analyse(self, research: dict[str, Any], usable_evidence: list[dict[str, Any]]) -> dict[str, Any]:
        self.received_evidence = usable_evidence
        return self.response


def llm_response(decision: str = "RESEARCH_ONLY", status: str = "llm_analysis_complete") -> dict[str, Any]:
    return {
        "status": status,
        "analysis": {"decision": decision},
        "unsupported_claims": [],
        "publication_allowed": False,
    }


def good_collection() -> dict[str, Any]:
    return {
        "records": [{
            "record_id": "match-record-1",
            "source": "unit-test",
            "source_url": "https://example.invalid/source",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "facts": {
                "home_team": "Atletico-MG",
                "away_team": "Cruzeiro",
                "competition": "Brazil Serie A",
                "kickoff": "2026-10-29T23:30:00",
                "source_ref": "unit-test-record",
            },
            "raw_payload": {
                "supporting_signals": ["A recorded supporting signal."],
                "against_signals": ["A recorded counter-signal."],
            },
        }]
    }


class LocalLLMPipelineTests(unittest.TestCase):
    def setUp(self):
        self.fixture = {
            "home_team": "Atletico-MG",
            "away_team": "Cruzeiro",
            "competition": "Brazil Serie A",
            "kickoff": "2026-10-29T23:30:00",
        }

    def test_llm_can_downgrade_deterministic_research(self):
        llm = FakeLLM(llm_response(decision="INSUFFICIENT_EVIDENCE"))
        result = MatchSieveAgentPipeline(llm_client=llm).run(
            good_collection(), self.fixture, "RESULT_1X2"
        )
        self.assertEqual(result["pipeline_status"], "insufficient_evidence")
        self.assertEqual(len(llm.received_evidence), 1)

    def test_llm_cannot_upgrade_deterministic_quality_failure(self):
        llm = FakeLLM(llm_response(decision="RESEARCH_ONLY"))
        result = MatchSieveAgentPipeline(llm_client=llm).run(
            {"records": []}, self.fixture, "RESULT_1X2"
        )
        self.assertEqual(result["pipeline_status"], "insufficient_evidence")
        self.assertEqual(llm.received_evidence, [])

    def test_invalid_llm_citations_force_review(self):
        llm = FakeLLM(llm_response(status="review_required"))
        result = MatchSieveAgentPipeline(llm_client=llm).run(
            good_collection(), self.fixture, "RESULT_1X2"
        )
        self.assertEqual(result["pipeline_status"], "review_required")

    def test_llm_is_optional(self):
        result = MatchSieveAgentPipeline().run(
            good_collection(), self.fixture, "RESULT_1X2"
        )
        self.assertIsNone(result["llm_analysis"])
        self.assertEqual(result["pipeline_status"], "ready_for_human_review")


if __name__ == "__main__":
    unittest.main()
