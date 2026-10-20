# Provider & Source Catalogue

Provider network access is disabled by default. The catalog is an inventory, not a claim that every source is currently available, free, complete or suitable for every competition.

## Previously listed in the original ZIP

| Key | Secret variable | Status in this foundation |
|---|---|---|
| `sportmonks` | `SPORTMONKS_API_TOKEN` | Catalogued; old adapter not copied; needs a new contract/coverage test. |
| `football_data_org` | `FOOTBALL_DATA_ORG_TOKEN` | Working-shape adapter included, but API key, free limits, target competitions and schema must be smoke-tested. |
| `footballdata_io` | `FOOTBALLDATA_IO_API_KEY` | Catalogued; old adapter is unverified. |
| `livefootball` | `LIVEFOOTBALL_API_KEY` | Catalogued; old adapter is unverified. |
| `sportscore` | `SPORTSCORE_API_KEY` | Adapter for documented v1 daily fixtures included; verify live payload and competition coverage. |
| `clearsports` | `CLEARSPORTS_API_KEY` | Catalogued; old adapter unverified. |
| `the_odds_api` | `THE_ODDS_API_KEY` | Optional odds only; not needed for archive calculations. |
| `openweather` | `OPENWEATHER_API_KEY` | Optional, low priority. |

## Additional candidates

- **Football-Data.co.uk CSV:** local import works for common column names and preserves all extra input columns as observations. Historical results/odds/statistics vary by league/season. Not a live fixture API.
- **SportScore:** current public docs describe a no-key fixture endpoint by UTC date, up to 200 items, and require an attribution link for its free public API. This foundation's adapter is unverified until a live smoke test; commercial/high-volume use may require provider confirmation.
- **OpenLigaDB:** no-key adapter included for the league/season route; coverage is competition-dependent and is not expected to supply the whole worldwide slate.

Useful public references at build time:
- Football-Data.co.uk downloads: https://www.football-data.co.uk/downloadm.php
- SportScore API: https://sportscore.com/developers/api/
- SportScore terms: https://sportscore.com/developers/terms/
- OpenLigaDB docs: https://api.openligadb.de/index.html
- Football-Data.org docs: https://www.football-data.org/documentation/quickstart

## Adapter decision rule

Before enabling a source, test it for just one day and one target competition. Record: configured plan/limits, records received, upcoming-fixture coverage, score/statistic field coverage, date/time format, missing values, failure rates, source timestamps and observed costs. Run repeat requests to check duplicates and whether the response updates. Keep providers disabled until a human chooses them in `.env`.

## Why there is no automatic provider waterfall

Silent fallback can make fixtures appear complete when a lower-quality source returned only some of the requested data. It also makes it hard to know which source supplied an observation. Select the provider for each ingestion run, log the result, preserve the raw payload and compare coverage. We can add a source router after actual tests identify complementary sources.
