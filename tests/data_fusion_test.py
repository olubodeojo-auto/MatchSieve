from services.match_builder import MatchBuilder
from services.data_fusion import DataFusion

builder = MatchBuilder()

matches = builder.build_today()

fusion = DataFusion()

match = fusion.merge(matches[0])

print(match.to_dict())