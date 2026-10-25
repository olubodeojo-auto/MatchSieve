from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from matchsieve.agents.pipeline import MatchSieveAgentPipeline
from matchsieve.kb_writer import refresh_indexes
from matchsieve.repository import Repository


class PipelineQualityGateTests(unittest.TestCase):
    def _record(self, *, good: bool = True) -> dict:
        facts = {
            "home_team": "Alpha FC",
            "away_team": "Beta FC",
            "competition": "Test Premier Division",
            "kickoff": "2026-10-25T14:00:00Z",
        }
        if not good:
            facts.pop("kickoff")
        return {
            "record_id": "record-good" if good else "record-incomplete",
            "source": "offline-test",
            "source_url": "https://example.test/match/alpha-beta",
            "source_ref": "alpha-beta-2026-10-25",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "facts": facts,
            "raw_payload": {
                "supporting_signals": ["Alpha scored in 8 of its last 10 completed matches."],
                "against_signals": ["Alpha failed to score in 2 of those matches."],
            },
        }

    def test_pipeline_uses_quality_gate_and_keeps_counter_evidence(self):
        record = self._record()
        collection = {"status": "success", "records": [record], "records_collected": 1}
        fixture = {
            "home_team": "Alpha FC",
            "away_team": "Beta FC",
            "competition": "Test Premier Division",
            "kickoff": "2026-10-25T14:00:00Z",
        }

        result = MatchSieveAgentPipeline().run(
            collection, fixture, "OVER_UNDER_MATCH_GOALS", advice_requested=False
        )

        self.assertEqual(result["quality"]["usable"], 1)
        self.assertEqual(result["research"]["recommendation"]["status"], "RESEARCH_ONLY")
        self.assertTrue(result["research"]["supporting_evidence"])
        self.assertTrue(result["research"]["counter_evidence"])
        self.assertFalse(result["research"]["probabilities_displayed"])
        self.assertEqual(result["pipeline_status"], "ready_for_human_review")
        self.assertIn("What challenges it", result["report"]["markdown"])

    def test_incomplete_record_is_excluded_and_cannot_produce_a_lean(self):
        record = self._record(good=False)
        collection = {"status": "partial", "records": [record], "records_collected": 1}
        fixture = {"home_team": "Alpha FC", "away_team": "Beta FC"}

        result = MatchSieveAgentPipeline().run(
            collection, fixture, "OVER_UNDER_MATCH_GOALS"
        )

        self.assertEqual(result["quality"]["insufficient"], 1)
        self.assertEqual(result["research"]["recommendation"]["status"], "PASS_INSUFFICIENT_EVIDENCE")
        self.assertIsNone(result["research"]["recommendation"]["lean"])
        self.assertEqual(len(result["research"]["excluded_evidence"]), 1)
        self.assertEqual(result["pipeline_status"], "insufficient_evidence")


class KnowledgeBaseSmokeTests(unittest.TestCase):
    def test_fixture_snapshot_and_markdown_indexes_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "matchsieve-test.sqlite3"
            repo = Repository(db_path)
            fixture_id = repo.add_fixture(
                {
                    "competition": "Test Premier Division",
                    "kickoff_utc": "2026-10-25T14:00:00Z",
                    "home_team": "Alpha FC",
                    "away_team": "Beta FC",
                    "status": "scheduled",
                },
                source_key="offline-test",
                source_ref="alpha-beta-2026-10-25",
                source_url="https://example.test/match/alpha-beta",
                raw_payload={"fixture_source": "offline-test", "test_record": True},
            )

            indexes = refresh_indexes(repo)
            index_text = Path(indexes["index"]).read_text(encoding="utf-8")
            fixture_index_text = Path(indexes["fixtures_index"]).read_text(encoding="utf-8")

            self.assertGreater(fixture_id, 0)
            self.assertIn("Alpha FC vs Beta FC", index_text)
            self.assertIn("offline-test", index_text)
            self.assertIn("Alpha FC vs Beta FC", fixture_index_text)
            self.assertIn("knowledge-base", str(Path(indexes["index"])))
            conn = __import__("matchsieve.db", fromlist=["connect"]).connect(db_path)
            try:
                fixture_count = conn.execute("SELECT COUNT(*) FROM fixtures").fetchone()[0]
                snapshot_count = conn.execute("SELECT COUNT(*) FROM source_snapshots").fetchone()[0]
            finally:
                conn.close()
            self.assertEqual(fixture_count, 1)
            self.assertEqual(snapshot_count, 1)


if __name__ == "__main__":
    unittest.main()
