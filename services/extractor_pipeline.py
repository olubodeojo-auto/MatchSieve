from services.feature_factory import FeatureFactory
from services.feature_enricher import FeatureEnricher

from extractors.goal_extractor import GoalExtractor
from extractors.attack_extractor import AttackExtractor
from extractors.defence_extractor import DefenceExtractor
from extractors.market_extractor import MarketExtractor
from extractors.form_extractor import FormExtractor
from extractors.league_extractor import LeagueExtractor
from extractors.live_extractor import LiveExtractor
from extractors.weather_extractor import WeatherExtractor
from extractors.h2h_extractor import H2HExtractor
from extractors.risk_extractor import RiskExtractor
from extractors.tactical_extractor import TacticalExtractor


class ExtractorPipeline:

    def __init__(self):

        self.factory = FeatureFactory()
        self.enricher = FeatureEnricher()

        self.extractors = [

            GoalExtractor(),
            AttackExtractor(),
            DefenceExtractor(),
            MarketExtractor(),
            FormExtractor(),
            LeagueExtractor(),
            LiveExtractor(),
            WeatherExtractor(),
            H2HExtractor(),
            RiskExtractor(),
            TacticalExtractor()

        ]

    def process(self, match):

        features = self.factory.build(match)

        for extractor in self.extractors:

            features = extractor.extract(match, features)

        features = self.enricher.enrich(features)

        return features