# MatchSieve Architecture

## Components

- **Browser UI** (`web/`): fixture search, market choice, report display/history and local operator actions.
- **HTTP API** (`matchsieve/webserver.py`): Python standard-library HTTP server exposing browser and `/api/mobile/*` routes.
- **Research/domain layer** (`matchsieve/analytics.py`, `reporting.py`): deterministic market-oriented evidence summaries and report status.
- **Archive/repository** (`db.py`, `repository.py`): SQLite canonical records, results, raw source snapshots, provider runs, report history and knowledge documents.
- **Ingest/import** (`importers.py`, `inbox_sync.py`, `normalise.py`): CSV/JSON normalisation, upserts, hash-ledger sync and source metadata.
- **Provider boundary** (`provider_manager.py`, `providers/`): explicit one-provider fetches for three included adapters; source catalogue includes other candidates without pretending they are wired.
- **Knowledge base** (`knowledge-base/`, `kb_writer.py`): searchable documentation, templates and saved report artefacts.
- **Android** (`../MatchSieve-Mobile/`): Compose client with Retrofit API interface and ViewModel; server owns fixture/report IDs and all analysis.

## Data flow

`provider fetch or manual/CSV/JSON import → source snapshot + canonical fixture/result rows → deterministic evidence generation for selected fixture and market → saved report record → web/mobile report rendering`

Report generation must never infer missing facts from the LLM. Optional Ollama commentary receives only an evidence payload when enabled. A generated report is an archive snapshot; it does not refresh the underlying match data automatically.

## Boundary and risk

The default server listens on loopback and is local-development only. It currently has no customer authentication, authorization or subscription enforcement. Operator routes are write-capable. Do not expose it to the public internet. For paid production, introduce secure accounts/session middleware, role and report ownership enforcement, server-side billing entitlements, production server/runtime, HTTPS, rate limiting, request tracing, database migration/backup strategy and data source rights/freshness controls.

## Shared contract

`docs/API_CONTRACT.md` documents routes and key schema. Android model mapping is in `MatchSieve-Mobile/app/src/main/java/com/matchsieve/mobile/data/Models.kt`. Changes to either side need tests on both sides.
