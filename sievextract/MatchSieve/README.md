# MatchSieve — Web Research Desk + Local API (v0.3.0)

**What this is:** a working local football-research prototype with a browser interface, a Python/SQLite backend, deterministic evidence reports, import tools, a provider catalogue and an API contract shared with a separate Android client.

**What this is not:** not yet a public SaaS, not yet a paid product, and not yet safe to expose to the internet. Authentication, subscriptions/entitlements, production hosting/TLS, live provider acceptance testing, data licensing decisions, production operations and the mobile release build remain explicit launch gates. The `/api/status` payload reports `production_ready: false` on purpose.

## Customer journey

1. A researcher opens the MatchSieve research desk and searches stored fixtures.
2. They choose a fixture, then the market they want researched (for example Under 4.5, Over 2.5, BTTS, Double Chance, 1X2 context or a general brief).
3. The backend builds a report from records actually present in the local archive.
4. The report distinguishes supporting signals, counter-signals, missing information and source provenance. Sparse data produces `LIMITED_EVIDENCE`, not a made-up probability.
5. Reports are saved locally; the user can reopen history or export a Markdown report.

Operator controls for manual fixtures, CSV import and provider fetches are separated from the main customer flow in the UI. They are for local development only because they do not yet have administrator authentication.

## Implemented foundation

- Python standard-library server and SQLite archive.
- Fixture/results ingestion from CSV/JSON, including common Football-Data.co.uk columns; hash-ledger inbox sync and exports.
- Deterministic market-oriented evidence summaries and report versioning.
- Local knowledge-base indexing/search and source snapshots.
- Browser interface: fixture search, market selection, report generation, report details/history, Markdown download/copy, operator-side fixture/import/provider tools.
- API contract version `0.2`: fixtures, markets, research creation, report history/detail, source catalogue, knowledge search and operator fetch/import routes.
- Optional local Ollama commentary. Disabled by default; the deterministic evidence remains the ground truth.
- Three coded optional provider adapters: SportScore, Football-Data.org and OpenLigaDB. They are opt-in and are not certified as live-reliable merely because adapter code exists. Their licensing, target-competition coverage, source attribution and actual account/endpoint behaviour need specific validation.

## Quick start — Windows PowerShell

Use Python 3.11 or later. Core runtime uses the standard library.

```powershell
cd path\to\MatchSieve
Copy-Item .env.example .env
python run.py init
python run.py serve
```

Open `http://127.0.0.1:8765`. The default host binds to loopback. Keep it there for local development. Do not set it to `0.0.0.0` or expose this service publicly as-is.

### Bring in historical data

Place approved CSV/JSON source files into `data/inbox/`.

To exercise the customer journey without any API key, you may import `data/examples/SYNTHETIC_DEMO_ONLY.csv` explicitly:

```powershell
python run.py import-csv data/examples/SYNTHETIC_DEMO_ONLY.csv --source-key synthetic_demo
```

**Every team, fixture and score in that file is fictional test data. Never treat it as a real match or publish it as football information.** It is optional and is not auto-imported. To use real data, import a source you are permitted to use.

```powershell
python run.py sync-inbox
python run.py fixtures --limit 20
python run.py research --fixture-id 1 --market UNDER_4_5
python run.py providers
python run.py index-kb
python run.py export-fixtures
python run.py export-archive
```

The source URL, source key and capture timestamps should be retained where available. An import does not imply the source permits commercial redistribution. Review the terms of the source before using that data in paid customer-facing reports.

## Configuration and provider plug-ins

`.env.example` is a **safe template**, not a secret bundle. Make a private `.env` copy locally. Every provider is disabled unless explicitly listed in `MATCHSIEVE_ENABLED_PROVIDERS`. Only one provider is fetched when a user explicitly requests it; there is no silent multi-provider fan-out.

Example (after separately evaluating and authorising SportScore):

```dotenv
MATCHSIEVE_ENABLED_PROVIDERS=sportscore
SPORTSCORE_API_KEY=your_private_key_here
```

Then fetch one day at a time using the operator UI or:

```powershell
python run.py fetch --provider sportscore --date 2026-10-24 --status upcoming
```

Never type a real key into code, Android resources, screenshots or a repository. Never copy legacy `config/*_key.txt` files into this project or a distributable ZIP. This package intentionally does not contain live API credentials. If your original BojoSentinelAI `.env` has values you own and intend to reuse, copy only the required values into the local ignored `.env` after checking provider terms. The MatchSieve `MATCHSIEVE_*` variables take precedence; legacy `SENTINEL_*` values remain as fallback for selected settings.

## Run tests

```powershell
python -m compileall -q .
python -m unittest discover -s tests -v
node --check web/app.js
```

The Python test suite uses local databases and mocked/synthetic data. It must not need live API keys or internet access.

## Project map

- `matchsieve/` — archive, ingestion, analytics, report generation, provider adapters and HTTP server.
- `web/` — browser customer journey.
- `data/inbox/` — local input drop folder (contents ignored in Git/ZIP).
- `knowledge-base/` — generated indexes, templates and saved report destination.
- `migrations/` — initial schema migration reference.
- `tests/` — offline unit and API-contract tests.
- `docs/WEB_CUSTOMER_JOURNEY.md` — intended and current browser experience.
- `docs/MOBILE_CUSTOMER_JOURNEY.md` — matching Android experience.
- `docs/API_CONTRACT.md` — exact local JSON routes shared with Android.
- `docs/INTEGRATION_READINESS.md` — honest provider/plug-in status and setup.
- `CODEX_HANDOFF.md` — ordered audit and wiring plan for the developer tool.

The companion app lives separately in `../MatchSieve-Mobile/` or in the separate Android ZIP. Its default debug URL is Android Emulator's `http://10.0.2.2:8765/` and it must be configured to a secure HTTPS host for a production build. The default release URL `https://api.example.invalid/` is deliberately a sentinel placeholder that must be replaced before a usable release.
