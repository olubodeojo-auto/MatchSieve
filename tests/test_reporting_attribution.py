import unittest

from matchsieve.reporting import report_to_markdown


class ProviderAttributionTests(unittest.TestCase):
    def test_sportscore_attribution_is_present_in_markdown_exports(self):
        evidence = {
            "fixture": {"home_team": "Example Home", "away_team": "Example Away", "competition": "Synthetic League", "kickoff_utc": "2026-10-25T15:00:00Z"},
            "market": {"label": "Under 4.5 goals", "question": "Does the stored history support a low total-goal context?"},
            "status": "LIMITED_EVIDENCE", "generated_at": "2026-10-20T10:00:00Z",
            "home_form": {"team": "Example Home", "sample_size": 0},
            "away_form": {"team": "Example Away", "sample_size": 0},
            "supporting_signals": [], "counter_signals": [], "h2h": [],
            "missing_information": ["Synthetic test data only"],
            "sources": [{"source_key": "sportscore", "captured_at": "2026-10-20T09:00:00Z", "source_ref": "test-fixture", "source_url": "https://sportscore.com/", "quality_label": "test"}],
            "method_note": "Test-only evidence; not a probability."
        }
        markdown = report_to_markdown(evidence)
        self.assertIn("Powered by SportScore", markdown)
        self.assertIn("https://sportscore.com/", markdown)


if __name__ == "__main__":
    unittest.main()
