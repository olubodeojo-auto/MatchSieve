"""Manual smoke script for match data fusion; not an automated pytest test."""
def main():
    from services.match_builder import MatchBuilder
    from services.data_fusion import DataFusion
    matches = MatchBuilder().build_today()
    if not matches:
        raise SystemExit("No fixtures loaded. Configure an available provider or fixture dataset first.")
    print(DataFusion().merge(matches[0]).to_dict())
if __name__ == "__main__":
    main()
