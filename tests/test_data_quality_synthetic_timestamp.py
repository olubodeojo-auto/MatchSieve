from __future__ import annotations

import unittest
from datetime import datetime, timezone

from matchsieve.agents.data_quality import DataQualityAgent


class SyntheticTimestampQualityTests(unittest.TestCase):
    def test_synthetic_demo_timestamp_cannot_be_marked_usable(self):
        collection = {
            "records": [{
                "record_id": "demo-record",
                "source": "user_supplied_excerpt",
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "facts": {
                    "home_team": "Atletico-MG",
                    "away_team": "Cruzeiro",
                    "competition": "Brazil Serie A",
                    "kickoff": "2026-10-29 23:30",
                },
                "raw_payload": {"capture_timestamp_is_synthetic": True},
            }]
        }
        result = DataQualityAgent().assess(collection)
        assessment = result["assessments"][0]
        self.assertEqual(assessment["quality_label"], "review")
        self.assertTrue(any("synthetic demo metadata" in warning for warning in assessment["warnings"]))


if __name__ == "__main__":
    unittest.main()
