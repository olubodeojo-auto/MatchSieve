import unittest

from engines.confidence_engine import ConfidenceEngine
from engines.form_engine import FormEngine
from extractors.form_extractor import FormExtractor
from extractors.risk_extractor import RiskExtractor
from models.analysis_context import AnalysisContext
from models.football_features import FootballFeatures
from services.feature_factory import FeatureFactory
from services.normalized_match import NormalizedMatch


class LegacyFeatureAuditTests(unittest.TestCase):
    def test_form_markers_are_converted_to_points(self):
        match = NormalizedMatch()
        match.home_form = ["W", "D", "L", "W", "W"]
        match.away_form = ["L", "D", "L", "D", "W"]
        features = FormExtractor().extract(match, FootballFeatures())

        self.assertEqual(features.home_last5, [3, 1, 0, 3, 3])
        self.assertEqual(features.away_last5, [0, 1, 0, 1, 3])
        self.assertEqual(features.home_form_score, 10)
        self.assertEqual(features.away_form_score, 5)

        result = FormEngine().calculate(AnalysisContext(features=features))
        self.assertEqual(result["home_points"], 10)
        self.assertEqual(result["away_points"], 5)
        self.assertEqual(result["difference"], 5)
        self.assertEqual(result["rating"], "HOME STRONG")

    def test_unknown_form_values_are_ignored_without_crashing(self):
        match = NormalizedMatch()
        match.home_form = ["W", "UNKNOWN", "D"]
        match.away_form = []
        features = FormExtractor().extract(match, FootballFeatures())

        self.assertEqual(features.home_last5, [3, 1])
        self.assertEqual(features.away_last5, [])
        self.assertEqual(features.home_form_score, 4)

    def test_risk_extractor_does_not_claim_perfect_data_or_agreement(self):
        match = NormalizedMatch()
        match.home_team = "Alpha FC"
        match.away_team = "Beta FC"
        match.league = "Test League"
        match.provider = "one_provider"
        features = RiskExtractor().extract(match, FootballFeatures())

        self.assertLess(features.data_quality, 100)
        self.assertEqual(features.provider_agreement, 0)

    def test_confidence_is_zero_when_no_evidence_exists(self):
        features = FootballFeatures()
        result = ConfidenceEngine().calculate(AnalysisContext(features=features))
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["reasons"], [])

    def test_feature_factory_carries_fixture_metadata(self):
        match = NormalizedMatch()
        match.fixture_id = "fixture-1"
        match.venue = "Test Ground"
        match.kickoff = "2026-10-20T18:00:00Z"
        match.status = "SCHEDULED"
        features = FeatureFactory().build(match)

        self.assertEqual(features.fixture_id, "fixture-1")
        self.assertEqual(features.venue, "Test Ground")
        self.assertEqual(features.kickoff, "2026-10-20T18:00:00Z")
        self.assertEqual(features.status, "SCHEDULED")
        self.assertEqual(features.data_quality, 0)
        self.assertEqual(features.provider_agreement, 0)


if __name__ == "__main__":
    unittest.main()
