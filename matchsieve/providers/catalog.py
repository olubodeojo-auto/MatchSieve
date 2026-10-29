"""MatchSieve provider inventory. Live status is established by real responses, not registration alone."""
PROVIDERS = [
    {"key": "api_football", "label": "API-Football", "kind": "rest_api", "env_key": "API_FOOTBALL_KEY", "status": "live_connection_seen_user_reported_http_200", "data_types": ["fixtures", "scores", "leagues", "teams", "statistics"], "note": "Free plan quota is 100 requests/day according to the user's dashboard; confirm current quota in the account."},
    {"key": "thesportsdb", "label": "TheSportsDB", "kind": "rest_api", "env_key": "THESPORTSDB_API_KEY", "status": "free_v1_key_available_live_response_not_yet_checked", "data_types": ["fixtures", "events", "teams", "leagues"], "note": "Free v1 shared key is 123; schedule times and coverage may be incomplete."},
    {"key": "sportmonks", "label": "SportMonks", "kind": "rest_api", "env_key": "SPORTMONKS_API_TOKEN", "status": "live_connection_seen_user_reported_http_200", "data_types": ["fixtures", "scores", "statistics"], "note": "Existing key returned HTTP 200; initial check queried leagues, not fixtures."},
    {"key": "footballdata_io", "label": "FootballData.io", "kind": "rest_api", "env_key": "FOOTBALLDATA_IO_API_KEY", "status": "live_connection_seen_user_reported_http_200", "data_types": ["fixtures", "scores"], "note": "Existing key returned HTTP 200; returned records and schema still need confirmation."},
    {"key": "livefootball", "label": "LiveFootball", "kind": "rest_api", "env_key": "LIVEFOOTBALL_API_KEY", "status": "live_connection_seen_user_reported_http_200", "data_types": ["fixtures", "live"], "note": "Existing key returned HTTP 200; returned records and schema still need confirmation."},
    {"key": "sportscore", "label": "SportScore", "kind": "rest_api", "env_key": "SPORTSCORE_API_KEY", "status": "live_connection_seen_user_reported_http_200", "data_types": ["fixtures", "scores", "h2h", "standings"], "note": "Existing key returned HTTP 200 and a match record; check coverage and terms before commercial use."},
    {"key": "football_data_org", "label": "Football-Data.org", "kind": "rest_api", "env_key": "FOOTBALL_DATA_ORG_TOKEN", "status": "credential_not_configured", "data_types": ["fixtures", "scores", "standings"], "note": "Adapter available; no token was present during the user's local credential check."},
    {"key": "openligadb", "label": "OpenLigaDB", "kind": "rest_api", "env_key": None, "status": "adapter_available_coverage_limited", "data_types": ["fixtures", "scores", "standings"], "note": "No-key community API; coverage varies by league and season."},
    {"key": "the_odds_api", "label": "The Odds API", "kind": "rest_api", "env_key": "THE_ODDS_API_KEY", "status": "not_configured_optional", "data_types": ["odds"], "note": "Optional odds-only source."},
    {"key": "openweather", "label": "OpenWeather", "kind": "rest_api", "env_key": "OPENWEATHER_API_KEY", "status": "not_configured_optional", "data_types": ["weather"], "note": "Optional context; not needed for fixture intake."},
    {"key": "clearsports", "label": "ClearSports", "kind": "rest_api", "env_key": "CLEARSPORTS_API_KEY", "status": "not_configured_unverified", "data_types": ["fixtures", "statistics"], "note": "Legacy code not connected to the current provider manager."},
    {"key": "football_data_co_uk", "label": "Football-Data.co.uk CSV", "kind": "local_csv", "env_key": None, "status": "local_import_only", "data_types": ["historical_results", "some_historical_odds", "some_statistics"], "note": "Historical CSV import, not a live API."},
]


def list_providers():
    return [dict(provider) for provider in PROVIDERS]
