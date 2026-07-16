from services.match_builder import MatchBuilder
from services.data_fusion import DataFusion
from services.feature_factory import FeatureFactory
from services.feature_enricher import FeatureEnricher

builder = MatchBuilder()

matches = builder.build_today()

fusion = DataFusion()

match = fusion.merge(matches[0])

factory = FeatureFactory()

features = factory.build(match)

enricher = FeatureEnricher()

features = enricher.enrich(features)

print(features.to_dict())