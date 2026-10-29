"""Manual smoke script for feature generation; not an automated pytest test."""
def main():
    from services.match_builder import MatchBuilder
    from services.data_fusion import DataFusion
    from services.feature_factory import FeatureFactory
    matches = MatchBuilder().build_today()
    if not matches:
        raise SystemExit("No fixtures loaded. Configure an available provider or fixture dataset first.")
    match = DataFusion().merge(matches[0])
    print(FeatureFactory().build(match).to_dict())
if __name__ == "__main__":
    main()
