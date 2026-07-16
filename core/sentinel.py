from services.feature_factory import FeatureFactory
from services.feature_enricher import FeatureEnricher
from engines.master_engine import MasterEngine
from models.context import Context


class Sentinel:

    def __init__(self):

        self.factory = FeatureFactory()
        self.enricher = FeatureEnricher()
        self.master = MasterEngine()

    def analyze(self, fixture_id):

        context = Context()

        # Build Features
        features = self.factory.build(fixture_id)

        if features is None:
            return None

        # Enrich Features
        features = self.enricher.enrich(features)

        # Store Features
        context.features = features

        # Run All AI Engines
        self.master.analyze(context)

        return context