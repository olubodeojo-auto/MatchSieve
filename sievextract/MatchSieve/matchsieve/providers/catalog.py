"""Source inventory informed by the previous BojoSentinelAI ZIP. Statuses are intentionally explicit."""
PROVIDERS=[
 {"key":"sportmonks","label":"SportMonks","kind":"rest_api","env_key":"SPORTMONKS_API_TOKEN","status":"legacy_candidate_unverified","data_types":["fixtures","scores","statistics"],"note":"Legacy adapter exists in the old ZIP but should be smoke-tested before reuse."},
 {"key":"football_data_org","label":"Football-Data.org","kind":"rest_api","env_key":"FOOTBALL_DATA_ORG_TOKEN","status":"adapter_available_test_before_use","data_types":["fixtures","scores","standings"],"note":"Implemented in the new project as an optional fixture/results adapter; token and league coverage must be verified."},
 {"key":"footballdata_io","label":"FootballData.io","kind":"rest_api","env_key":"FOOTBALLDATA_IO_API_KEY","status":"legacy_candidate_unverified","data_types":["fixtures","scores"],"note":"Legacy adapter exists in old ZIP; endpoint behaviour/subscription needs confirmation."},
 {"key":"livefootball","label":"LiveFootball","kind":"rest_api","env_key":"LIVEFOOTBALL_API_KEY","status":"legacy_candidate_unverified","data_types":["fixtures","live"],"note":"Legacy adapter exists in old ZIP; not enabled by default."},
 {"key":"sportscore","label":"SportScore","kind":"rest_api","env_key":"SPORTSCORE_API_KEY","status":"adapter_available_smoke_test_required","data_types":["fixtures","scores","h2h","standings"],"note":"Public API docs describe day fixtures; verify coverage, terms, schema, stability, and visible attribution requirement before selecting it."},
 {"key":"clearsports","label":"ClearSports","kind":"rest_api","env_key":"CLEARSPORTS_API_KEY","status":"legacy_candidate_unverified","data_types":["fixtures","statistics"],"note":"Legacy adapter exists in old ZIP; not enabled by default."},
 {"key":"the_odds_api","label":"The Odds API","kind":"rest_api","env_key":"THE_ODDS_API_KEY","status":"optional_odds_only_unverified","data_types":["odds"],"note":"Optional market data only; never required for a historical evidence report."},
 {"key":"openweather","label":"OpenWeather","kind":"rest_api","env_key":"OPENWEATHER_API_KEY","status":"optional_context_unverified","data_types":["weather"],"note":"Optional and low priority; not needed for initial launch."},
 {"key":"football_data_co_uk","label":"Football-Data.co.uk CSV","kind":"local_csv","env_key":None,"status":"import_supported_source_scope_limited","data_types":["historical_results","some_historical_odds","some_statistics"],"note":"Downloaded CSV import supported. Not a live schedule API; record file, season, import time and source URL."},
 {"key":"openligadb","label":"OpenLigaDB","kind":"rest_api","env_key":None,"status":"adapter_available_competition_coverage_limited","data_types":["fixtures","scores","standings"],"note":"No-key community API adapter included; coverage depends on league/season and must be tested."},
]

def list_providers(): return [dict(p) for p in PROVIDERS]
