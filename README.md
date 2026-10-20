# MatchSieve

MatchSieve is the football research and intelligence platform being developed from the earlier BojoSentinelAI source. The repository keeps the original analysis engines, extractors, providers, and knowledge files available for controlled reuse while the product is organised around a tested data-ingestion and reporting foundation.

## Project setup

- **GitHub:** https://github.com/olubodeojo-auto/MatchSieve
- **Supabase project:** https://supabase.com/dashboard/project/iylsskasalkshfwcsafr
- **Supabase project ref:** `iylsskasalkshfwcsafr`
- **Supabase API URL:** `https://iylsskasalkshfwcsafr.supabase.co`
- **Supabase region:** Frankfurt (`eu-central-1`)

The Supabase project is newly created. No schema or data has been migrated into it yet. The v0.3.0 web foundation uses a local SQLite archive for its initial, offline-first workflow; do not point production data at Supabase until the schema and migration plan have been reviewed.

## Development priorities

1. Preserve the legacy provider integrations and analysis engines for testing, but treat their outputs as unverified until they pass controlled tests.
2. Establish repeatable fixture intake, source provenance, local archive, and report generation.
3. Keep credentials in an ignored local `.env` or local ignored config files. Never commit provider keys, Supabase service-role keys, or real customer data.
4. Add automated tests before wiring legacy engines into the new report pipeline.
5. Build the football knowledge base from source-attributed records; do not treat empty JSON files or unverified predictions as validated knowledge.

## Starting point

The clean MatchSieve v0.3.0 web foundation package and its build-verification notes are maintained separately from the legacy source. See `docs/MATCHSIEVE_V0_3_SETUP.md` for the handoff and next steps. Do not claim production readiness: authentication, tenant isolation, billing, live-provider rights and coverage, rate limits, monitoring, backups, privacy/terms, and mobile release validation remain open.
