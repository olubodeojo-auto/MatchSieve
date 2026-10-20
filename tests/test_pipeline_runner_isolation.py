import unittest
from unittest.mock import patch

from core.pipeline_runner import PipelineRunner
from models.football_features import FootballFeatures
from services.normalized_match import NormalizedMatch


def make_match(home, away, provider):
    match = NormalizedMatch()
    match.home_team = home
    match.away_team = away
    match.league = "Isolation Test League"
    match.provider = provider
    return match


class PipelineRunnerIsolationTests(unittest.TestCase):
    def test_sequential_fixtures_do_not_reuse_previous_fusion_state(self):
        runner = PipelineRunner()
        with patch.object(runner.extractors, "process", side_effect=lambda _match: FootballFeatures()), \
             patch.object(runner.master, "analyze", return_value={}):
            first = runner.analyze_match(make_match("Alpha FC", "Beta FC", "provider_a"))
            second = runner.analyze_match(make_match("Gamma FC", "Delta FC", "provider_b"))

        self.assertEqual(first.match.home_team, "Alpha FC")
        self.assertEqual(first.match.away_team, "Beta FC")
        self.assertEqual(second.match.home_team, "Gamma FC")
        self.assertEqual(second.match.away_team, "Delta FC")
        self.assertEqual(second.match.providers, ["provider_b"])
        self.assertNotIn("provider_a", second.match.raw_data)


if __name__ == "__main__":
    unittest.main()
