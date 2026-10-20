# Integrations and Plug-in Readiness

This file separates code that exists from services that are connected, licensed or verified. “Adapter included” must never be presented as “integration is production-ready.”

## Status table

| Integration/source | Current code state | Key / network required | Launch decision |
|---|---|---|---|
| Local CSV importer | Implemented; offline tests pass | No API key; a permitted source file is needed | Use for controlled historical ingestion after reuse rights review |
| Local JSON importer | Implemented; offline tests pass | No API key | Use for documented/manual imports |
| SportScore | Adapter included; one mapped payload tested; live smoke test outstanding | Optional `SPORTSCORE_API_KEY`; provider calls disabled by default | Verify the selected competition/date, pagination, rate limits, terms and visible attribution obligation; then test a single date |
| Football-Data.org | Adapter included; live schema/coverage not validated in this environment | `FOOTBALL_DATA_ORG_TOKEN` | Verify permitted competition coverage, auth, date windows, quotas, commercial display and attribution before use |
| OpenLigaDB | Adapter included; mapping test passes; coverage varies | No API key in the current adapter | Verify league/season coverage and availability on selected dates; decide whether it adds launch value |
| SportMonks | Catalogue only in MatchSieve | `SPORTMONKS_API_TOKEN` | Not wired to an active adapter in this project; do not assume the old ZIP code/key remains valid |
| FootballData.io | Catalogue only | `FOOTBALLDATA_IO_API_KEY` | Not wired to an active adapter |
| LiveFootball | Catalogue only | `LIVEFOOTBALL_API_KEY` | Not wired to an active adapter |
| ClearSports | Catalogue only | `CLEARSPORTS_API_KEY` | Not wired to an active adapter |
| The Odds API | Catalogue only | `THE_ODDS_API_KEY` | Odds-only candidate, no current adapter; defer until the core market reports are proven useful |
| OpenWeather | Catalogue only | `OPENWEATHER_API_KEY` | Low priority, no current adapter |
| Ollama local commentary | Optional HTTP client included; disabled by default | Local Ollama service + locally downloaded model | Local only; test output discipline and service availability, keep deterministic evidence separate |
| Billing/Stripe | Not implemented | Requires commercial account configuration | Blocker to paid SaaS launch; do not invent credentials/webhooks. Validate business-country eligibility and taxes first |
| Authentication/account service | Not implemented | A selected identity backend and server-side policy | Blocker to public SaaS launch |
| Production hosting/API domain | Not implemented | Domain, secret store, TLS, deploy and operations | Blocker to production mobile release and remote customers |

## Provider rules

1. `MATCHSIEVE_ENABLED_PROVIDERS` is empty in `.env.example`; the package therefore makes no live provider calls by default.
2. Explicitly enabling a provider is an operator choice. Do not enable multiple providers just to get a green status light.
3. Make one small date/competition request; inspect status, response shape, duplicate handling, coverage, timestamps and logs.
4. Capture source key, provider reference/URL where allowed, timestamp and raw snapshot. Mark the report limited if critical inputs are absent or stale.
5. Check commercial rights and attribution requirements before using data in a paid product. Technical access is not a redistribution licence.
6. Provider secrets belong only in the ignored local `.env` or a deployment secret store. Never put them in web JavaScript, Android BuildConfig, checked-in files, project ZIPs or screenshots.

## Required Codex work

- Add provider-level deterministic mock tests, timeout and error handling; verify endpoint parameters against current official docs.
- Add a per-provider freshness/coverage policy and reject or flag records older than the policy allows.
- Add quota/rate-limit visibility and safe retry strategy. Do not make blind repeated requests.
- Build provider health checks that show “not configured”, “disabled”, “test required”, “configured but not smoke-tested”, “working for tested scope” and “failed” as distinct statuses.
- If enabling SportScore in customer reports, ensure the required attribution link is present wherever the provider’s terms require it; web UI and Markdown exports include the attribution link for records tagged `sportscore`; an equivalent clickable link is implemented in Android source. Codex must confirm it against current provider terms and a real device build.
