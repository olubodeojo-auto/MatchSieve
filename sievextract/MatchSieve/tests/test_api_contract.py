from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from matchsieve.analytics import MARKETS
from matchsieve.repository import Repository
from matchsieve.reporting import generate_report
from matchsieve.webserver import mobile_report_from_evidence, mobile_report_from_record


class MatchSieveMobileContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Repository(Path(self.temp.name) / "matchsieve-test.sqlite3")
        self.fixture_id = self.repo.add_fixture({
            "home_team": "Evidence United", "away_team": "Research City",
            "competition": "Contract Test League", "kickoff_utc": "2026-11-15T16:00:00Z",
        }, source_key="contract-test", source_ref="offline fixture test")

    def tearDown(self):
        self.temp.cleanup()

    def test_market_catalogue_contains_documented_codes(self):
        self.assertIn("UNDER_4_5", MARKETS)
        self.assertIn("BTTS", MARKETS)
        self.assertIn("RESEARCH_BRIEF", MARKETS)

    def test_mobile_report_serialization_has_required_customer_fields(self):
        with patch("matchsieve.kb_writer.refresh_indexes", return_value={}):
            generated = generate_report(self.fixture_id, "UNDER_4_5", repo=self.repo, use_ollama=False)
        report = mobile_report_from_evidence(
            generated["report_id"], generated["report"], generated["markdown"],
            generated["path"], generated["llm_used"], "UNDER_4_5",
        )
        for key in ("id", "report_id", "fixture", "market_code", "market_label", "status",
                    "summary", "supporting_evidence", "counter_evidence", "missing_data",
                    "source_records", "generated_at_utc", "markdown", "method_note"):
            self.assertIn(key, report)
        self.assertEqual(report["fixture"]["id"], self.fixture_id)
        self.assertEqual(report["market_code"], "UNDER_4_5")
        self.assertEqual(report["status"], "LIMITED_EVIDENCE")
        self.assertGreater(len(report["markdown"]), 100)

    def test_history_record_round_trip_preserves_report_identity(self):
        with patch("matchsieve.kb_writer.refresh_indexes", return_value={}):
            generated = generate_report(self.fixture_id, "RESEARCH_BRIEF", repo=self.repo, use_ollama=False)
        rows = self.repo.list_reports(10)
        self.assertEqual(len(rows), 1)
        detail = self.repo.get_report(generated["report_id"])
        self.assertIsNotNone(detail)
        mobile = mobile_report_from_record(detail)
        self.assertEqual(mobile["id"], generated["report_id"])
        self.assertEqual(mobile["fixture"]["home_team"], "Evidence United")
        self.assertEqual(mobile["market_code"], "RESEARCH_BRIEF")


if __name__ == "__main__":
    unittest.main()
