from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from matchsieve.agents.local_llm import LocalLLMClient, LocalLLMError


class FakeResponse:
    def __init__(self, body: dict):
        self.body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


class LocalLLMTests(unittest.TestCase):
    def setUp(self):
        self.research = {"market": "RESULT_1X2", "fixture": {"home_team": "Atletico-MG", "away_team": "Cruzeiro"}}
        self.evidence = [{"record_id": "r1", "facts": {"home_team": "Atletico-MG", "away_team": "Cruzeiro"}}]
        self.analysis = {
            "summary": "The evidence is mixed.",
            "supporting_points": [{"claim": "The home team won a listed previous meeting.", "evidence_record_ids": ["r1"]}],
            "counter_points": [],
            "data_quality_concerns": [],
            "market_assessment": "The evidence does not establish a safe outcome.",
            "limitations": ["Only one record supplied."],
            "decision": "RESEARCH_ONLY",
        }

    @patch("matchsieve.agents.local_llm.urlopen")
    def test_sends_request_to_local_ollama_and_validates_citations(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"message": {"content": json.dumps(self.analysis)}})
        result = LocalLLMClient(model="qwen2.5:7b").analyse(self.research, self.evidence)
        self.assertEqual(result["status"], "llm_analysis_complete")
        self.assertEqual(result["unsupported_claims"], [])
        self.assertFalse(result["publication_allowed"])
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["model"], "qwen2.5:7b")
        self.assertEqual(body["format"], "json")

    @patch("matchsieve.agents.local_llm.urlopen")
    def test_unknown_evidence_ids_flag_claim_and_block_publication(self, mock_urlopen):
        bad = dict(self.analysis)
        bad["supporting_points"] = [{"claim": "Unsupported statement.", "evidence_record_ids": ["made-up"]}]
        mock_urlopen.return_value = FakeResponse({"message": {"content": json.dumps(bad)}})
        result = LocalLLMClient().analyse(self.research, self.evidence)
        self.assertEqual(result["status"], "review_required")
        self.assertEqual(len(result["unsupported_claims"]), 1)
        self.assertFalse(result["publication_allowed"])

    def test_remote_or_cloud_endpoint_is_rejected(self):
        with self.assertRaises(LocalLLMError):
            LocalLLMClient(base_url="https://ollama.com/api")

    def test_no_usable_evidence_does_not_call_model(self):
        with patch("matchsieve.agents.local_llm.urlopen") as mock_urlopen:
            result = LocalLLMClient().analyse(self.research, [])
        mock_urlopen.assert_not_called()
        self.assertEqual(result["status"], "insufficient_evidence")

    @patch("matchsieve.agents.local_llm.urlopen")
    def test_malformed_model_response_is_rejected(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"message": {"content": "not json"}})
        with self.assertRaises(LocalLLMError):
            LocalLLMClient().analyse(self.research, self.evidence)


if __name__ == "__main__":
    unittest.main()
