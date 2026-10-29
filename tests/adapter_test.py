"""Manual smoke script for the FootballData.io adapter.

Retained for manual provider checks, not automated pytest tests.
Run directly only when credentials and fixture data are configured.
"""
def main():
    from providers.footballdata_io import FootballDataIO
    from services.adapters.footballdata_io_adapter import FootballDataIOAdapter
    data = FootballDataIO().fixtures()
    matches = data.get("data", {}).get("matches", [])
    if not matches:
        raise SystemExit("No FootballData.io matches returned; check credentials, API access, and date filters.")
    print(FootballDataIOAdapter.convert(matches[0]).to_dict())
if __name__ == "__main__":
    main()
