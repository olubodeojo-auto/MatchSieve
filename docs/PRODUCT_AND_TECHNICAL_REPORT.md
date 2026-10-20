# MatchSieve Product and Technical Report — current foundation

## Purpose

MatchSieve is an evidence-led football research product, built around selecting a fixture, selecting a market and getting a report that separates supporting evidence, counter-signals, missing information and source provenance. It is intended for paying researchers/publishers, not for a free unlimited livescore audience.

## This build contains

- The populated Python/SQLite ingestion, storage, market-evidence and report pipeline.
- A responsive web interface and a local API shared with a separate Kotlin/Jetpack Compose Android client.
- CSV/JSON import, report history, Markdown exports, source snapshots, local knowledge search and a provider catalogue.
- Three opt-in provider adapters with limited offline payload tests.
- Separate documented user journeys and a step-by-step Codex integration handoff.

## Validation

At the 20 October 2026 build, 18 offline Python tests pass; Python compile and JavaScript syntax checks pass. An HTTP smoke test on a disposable database exercised status/catalogue/assets, fixture creation, limited-evidence report generation and report history/detail. No provider network call was made. Android source tests were authored but no Gradle/SDK was available to run them, so an APK build is not claimed.

## Why it is not production-ready yet

The local HTTP server has no authentication/authorisation and the operator write endpoints must not be exposed publicly. Payment processing, user entitlements, production URL/TLS, source commercial rights, provider live validation, data freshness policy, operations/backup/security controls, legal documents and Android release build are outstanding. The status endpoint intentionally says `production_ready: false`.

## Critical rule

Do not add generic placeholder predictions or auto-enable providers to make the product look full. Empty history is a legitimate state. `LIMITED_EVIDENCE` must stay visible and must not be converted into a win probability. Use `CODEX_HANDOFF.md` for acceptance criteria.
