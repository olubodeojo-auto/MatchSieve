"""Manual smoke script for feature enrichment; not an automated pytest test."""
def main():
    from services.match_builder import MatchBuilder
    from services.data_fusion import DataFusion
    from services.feature_factory import FeatureFactory
    from services.feature_enricher import FeatureEnricher
    matches = MatchBuilder().build_today()
    if not matches:
        raise SystemExit("No fixtures loaded. Configure an available provider or fixture dataset first.")
    match = DataFusion().merge(matches[0])
    features = FeatureFactory().build(match)
    print(FeatureEnricher().enrich(features).to_dict())
if __name__ == "__main__":
    main()
