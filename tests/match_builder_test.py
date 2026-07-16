from services.match_builder import MatchBuilder

builder = MatchBuilder()

matches = builder.build_today()

print(f"Matches Loaded: {len(matches)}")

print()

print(matches[0].to_dict())