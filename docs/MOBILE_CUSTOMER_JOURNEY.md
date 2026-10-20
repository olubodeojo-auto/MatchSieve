# MatchSieve Mobile Customer Journey — Android

## Design principle

The Android app is a client for the same MatchSieve backend and report engine as the web. It must not duplicate analytics, invent fixture/statistical content locally, or ship provider credentials. A single backend contract keeps reports consistent across web and phone.

## Journey A — first open

1. App opens to the Research screen and attempts to load fixture and market catalogues.
2. Show a clear loading state while requests are outstanding.
3. If the API cannot be reached, show an actionable message about connection/API URL rather than a blank screen. Provide retry/refresh.
4. Do not require an account in the local foundation. Accounts and customer entitlements are a production gate, not simulated in the client.

## Journey B — research a fixture

1. Search the stored fixture list, debounce typing and allow selection of a specific match.
2. Choose an explicit market (Under 4.5, Over 2.5, BTTS, Under 3.5, Double Chance, 1X2 context or general research brief).
3. Enable local Ollama commentary only if the server has enabled and configured it. Do not offer this as a cloud-AI feature.
4. Tap Generate report; disable duplicate taps while loading.
5. Display report status (particularly `LIMITED_EVIDENCE`), summary, supporting evidence, counter-evidence, missing data, source records/timestamps and the method note.
6. Let the user return to fixture selection or open the report library.

## Journey C — report library

1. Load the saved report history from the backend.
2. Present fixture, market, generated timestamp and status.
3. On opening a row, fetch `/api/mobile/research/{reportId}` instead of silently generating a new report.
4. Handle deleted/unknown report and network failure without losing the research tab state.

## API/data responsibilities

- Retrofit routes mirror `/api/mobile/fixtures`, `/api/mobile/markets`, `/api/mobile/research`, `/api/mobile/research/history` and `/api/mobile/research/{id}`.
- Report identifiers are backend-owned IDs. Do not substitute fixture ID for report ID.
- `LIMITED_EVIDENCE` remains visible. Null/unknown stats must not be rendered as zero.
- All paid access decisions must be enforced by backend entitlements after account/billing is integrated. Hiding a button in Android is not security.
- API URL is BuildConfig-supplied. Debug's default `10.0.2.2` is for the Android emulator only. Release uses `MATCHSIEVE_API_BASE_URL` or Gradle property `matchsieveApiBaseUrl`; replace the placeholder and require HTTPS before release.
- Do not place tokens, passwords, provider keys or private credentials in the APK.

## Required error and lifecycle behaviour

- Loading, no fixtures, no history, successful report, report generation error, connection error and HTTP authorization/rate-limit errors need distinct messaging.
- ViewModel owns screen state and coroutines; Compose UI observes that state.
- Do not log request bodies, secrets or user data in release builds. Debug HTTP logs are acceptable only against synthetic/local data.
- Respect Android lifecycle, network timeouts, and rotation/recreation. Add offline-friendly retry; do not display stale reports as current without a timestamp warning.

## Acceptance criteria

- Debug build installs on a supported emulator/device.
- Against a local seeded backend, app loads fixtures/markets, creates a report and reopens the same report from history.
- Unit tests cover JSON mapping for snake_case API fields and `LIMITED_EVIDENCE` report payloads.
- Release build uses HTTPS with a real service URL, has release logging disabled, retains shrinking rules required by Gson if applicable, and passes Android Lint/build checks.
- Customer account, consent/privacy, subscription status and server-side access entitlements are integrated before paid launch.
