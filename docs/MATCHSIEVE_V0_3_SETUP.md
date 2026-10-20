# MatchSieve v0.3.0 — setup and integration handoff

## What is already in place

- GitHub repository renamed to `olubodeojo-auto/MatchSieve`.
- A separate Supabase project exists at ref `iylsskasalkshfwcsafr` in `eu-central-1`.
- The repository retains the BojoSentinelAI analysis engines, extractors, provider modules, and knowledge files as legacy source for testing.
- The clean MatchSieve v0.3.0 web foundation package has been located in the project Library. Its package includes an offline-first Python/SQLite API, source-aware archive and knowledge-base workflow, reporting, provider adapters, docs, and tests.

## Important implementation boundary

The Supabase project is empty. Do not assume it is connected to the local SQLite API yet. First run and verify the v0.3.0 backend locally, then define and test the Supabase schema/migration separately. Never paste the Supabase service-role key into source code or commit it.

## Web foundation verification recorded with the package

- Python syntax and 24 offline Python tests passed in the package build environment.
- Browser JavaScript syntax check passed.
- HTTP integration tests covered fixture intake, markets, report generation, history/detail, disabled providers, and validation errors using disposable local databases.
- No live football-provider network calls were part of verification.
- All providers are disabled by default. The included active adapters are SportScore, Football-Data.org, and OpenLigaDB. Other catalogue entries are not active integrations.
- The Android project was not built because Gradle/Android SDK were unavailable in the build environment.

Treat these as package-reported verification, not as tests rerun on this machine.

## API and credential handling

Keep existing provider implementations available for controlled testing. Use only credentials you control, set them in a local ignored `.env`, and check provider plans, endpoint availability, quotas, and commercial-use terms before enabling live calls. If a credential was ever committed publicly, rotate it; deleting it in a later commit does not remove it from Git history.

## Recommended next steps in VS Code

1. Clone `https://github.com/olubodeojo-auto/MatchSieve.git` and open the folder.
2. Compare the legacy source directories with the clean v0.3.0 package before copying files into the repository. Avoid blindly overwriting files with matching names; keep the old engines until compatibility tests are in place.
3. Run the v0.3.0 offline test suite first and record the result in a commit.
4. Wire provider adapters behind explicit configuration and a disabled-by-default switch; test with fixture samples before live calls.
5. Document stable API contracts and evidence/provenance fields before adapting legacy engines.
6. Add a reviewed Supabase migration only after deciding which data belongs in PostgreSQL versus the local archive. Keep secrets and real user data out of Git.

## Not production-ready

Authentication, report ownership/tenant isolation, billing and server-side entitlements, production HTTPS hosting, source commercial rights, live provider coverage/freshness, rate limiting, monitoring/backups, privacy/terms, and Android release validation remain open.
