"""Manual smoke script for the match builder; not an automated pytest test."""
def main():
    from services.match_builder import MatchBuilder
    matches = MatchBuilder().build_today()
    print(f"Matches Loaded: {len(matches)}")
    if not matches:
        raise SystemExit("No fixtures loaded. Configure an available provider or fixture dataset first.")
    print(matches[0].to_dict())
if __name__ == "__main__":
    main()
