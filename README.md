# MatchSieve

MatchSieve is the football research and intelligence platform being developed from the earlier BojoSentinelAI source. The repository preserves the original analysis engines, extractors and provider integrations while the root project establishes a tested, local-first data-ingestion and reporting foundation.

## Project setup

- **GitHub:** https://github.com/olubodeojo-auto/MatchSieve
- **Supabase project:** https://supabase.com/dashboard/project/iylsskasalkshfwcsafr
- **Supabase project ref:** `iylsskasalkshfwcsafr`
- **Supabase API URL:** `https://iylsskasalkshfwcsafr.supabase.co`
- **Supabase region:** Frankfurt (`eu-central-1`)

The Supabase project is newly created. No schema or data has been migrated into it yet. The root v0.3.0 foundation uses a local SQLite archive for its initial offline-first workflow; do not point production data at Supabase until the schema and migration plan have been reviewed.

## Run the local research desk

Use Python 3.11 or later. From the repository root:

```powershell
Copy-Item .env.example .env
python run.py init
python run.py serve
```

Open `http://127.0.0.1:8765`. Keep the server bound to loopback for local development; do not expose it publicly as-is.

To run the offline test suite:

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
node --check web/app.js
```

## Development priorities

1. Preserve legacy provider integrations and analysis engines for controlled testing, but treat their outputs as unverified until they pass controlled tests.
2. Establish repeatable fixture intake, source provenance, local archive and report generation.
3. Keep credentials in an ignored local `.env` or local ignored config files. Never commit provider keys, Supabase service-role keys or real customer data.
4. Add automated tests before wiring legacy engines into the new report pipeline.
5. Build the football knowledge base from source-attributed records; do not treat empty JSON files or unverified predictions as validated knowledge.

## Audit and verification

- [`BUILD_VERIFICATION.md`](BUILD_VERIFICATION.md) — recorded local build/test evidence and explicit limits.
- [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) — phased audit plan and acceptance criteria.
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — current implementation status.
- [`docs/INTEGRATION_READINESS.md`](docs/INTEGRATION_READINESS.md) — provider and service readiness.

The nested `sievextract/MatchSieve/` directory is a separately preserved copy of the foundation package. Keep changes to the root runnable project and the nested copy deliberate; do not overwrite one with the other blindly.

Do not claim production readiness: authentication, tenant isolation, billing, live-provider rights and coverage, rate limits, monitoring, backups, privacy/terms and mobile release validation remain open.
