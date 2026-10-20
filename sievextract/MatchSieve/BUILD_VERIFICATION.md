# MatchSieve v0.3.0 — Build Verification

**Verification date:** 20 October 2026

## Results

- Python syntax: `python -m compileall -q .` — PASS.
- Python tests: `python -m unittest discover -s tests -v` — PASS (24 tests).
- Browser JavaScript parse check: `node --check web/app.js` — PASS.
- Local HTTP flow: PASS against a temporary SQLite database. Route tests cover status, mobile fixtures/markets/history/detail, provider catalogue, web assets, fixture creation, report generation with `LIMITED_EVIDENCE`, disabled-provider rejection without provider fan-out, and malformed JSON returning 400.
- Optional synthetic demo import: PASS — 13 explicitly fictional rows imported into a disposable database and a market report was generated. No demo data is auto-imported into a customer or default database.
- Provider network requests: NONE in the verification run. Adapter tests use mocked response payloads.
- Android: **NOT TESTED**. This environment has no Gradle installation or Android SDK. The Gradle wrapper JAR could not be downloaded because outbound DNS/network access was unavailable. Kotlin/Groovy build correctness and emulator/device behavior must be verified in Android Studio or a configured CI worker.

## Test inventory

The Python suite covers the API contract, canonical archive/normalisation/deduplication, CSV export, historical evidence calculations, HTTP API journeys, inbox hash-ledger sync, guarded optional Ollama commentary, provider payload mappings, provider catalog opt-in behavior and SportScore Markdown attribution.

## Important distinction

Passing local tests proves the tested local behaviors, not live feed availability, data licensing, production security, subscription billing, prediction calibration, or customer demand. See `docs/PROJECT_STATUS.md` and `CODEX_HANDOFF.md` for the remaining gates.
