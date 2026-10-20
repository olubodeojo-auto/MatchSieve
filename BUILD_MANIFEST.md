# MatchSieve Build Manifest

**Version:** 0.3.0 foundation
**Date:** 20 October 2026

## Web/backend package includes

- Python SQLite archive/repository, CSV/JSON import, inbox hash-ledger sync, data normalisation and archive exports.
- Deterministic market-oriented evidence engine and versioned report storage.
- HTTP browser/mobile API, report detail/history, provider catalogue and deliberately selected one-provider fetch flow.
- Responsive web research desk, report viewer/history, Markdown copy/download and local operator tools.
- Optional local Ollama client, disabled by default.
- Three optional provider adapters (SportScore, Football-Data.org, OpenLigaDB), plus historical CSV/JSON ingestion; live integrations remain gated. A 13-row fictional demo CSV is included for deliberate local UX testing and is never auto-imported.
- API contract tests, import/report/provider tests and offline setup documentation.
- Detailed web/mobile journeys, provider readiness matrix, architecture/status and Codex handoff.

## Android package includes

- Kotlin + Jetpack Compose user flow for fixture search/selection, market selection, report generation, report evidence, and saved reports.
- Retrofit interface, Gson wire models, configurable debug/release API base URL and a ViewModel using state flows/coroutines.
- Unit tests for fixture/report JSON mapping, including nullable scores and `LIMITED_EVIDENCE`.
- This execution environment has Java but no Gradle/Android SDK, so a compiled APK cannot be claimed from this build.

## Validation from this build

- `python -m compileall -q .`: passed.
- `python -m unittest discover -s tests -v`: 24 tests passed at the last execution.
- `node --check web/app.js`: passed.
- Local HTTP smoke test against a temporary SQLite database: status, empty fixture/market/history APIs, provider catalogue, web assets, manual fixture creation, report creation (`LIMITED_EVIDENCE`), history and report detail all passed. No live provider was contacted.
- Android unit tests are authored but unexecuted here due absent Gradle/Android SDK.

## Explicit exclusions

No `.env`, live keys, `config/*_key.txt`, `.git`, DB file, Python cache, live provider output or production build artefacts are included in the source ZIPs. The `.env.example` file uses blank placeholders only.

## Real production blockers

Customer authentication/authorisation and tenant data separation; billing and entitlement enforcement; selected-provider commercial rights and live validation; real production HTTPS host; request throttling; stale-data policy; backups/restore, monitoring, terms/privacy and support workflow; Android build/lint/release validation and end-to-end test on the deployed API.
