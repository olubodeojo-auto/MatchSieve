# Codex Handoff — MatchSieve Web + Android Integration Audit

**Mission:** audit this populated project and finish the wiring with the smallest safe changes. Do not rebuild it from scratch, replace working market analytics with mock output, delete tests to make builds green, or claim readiness without repeatable evidence. Preserve the customer's report workflow: fixture → market → research → explain evidence/limitations → save/open history.

## Workspace layout

- `MatchSieve/` — Python/SQLite server, analytics, importers, browser UI, documentation, provider adapters and tests.
- `MatchSieve-Mobile/` — separate Android Kotlin/Jetpack Compose client with Retrofit API client and ViewModel.
- `docs/API_CONTRACT.md` and the mobile typed models are the contract source. When changing a field, update both, add a regression test and keep the contract version deliberate.

## Phase 0 — baseline and safety (do first)

1. Run `python -m compileall -q .` and `python -m unittest discover -s tests -v` from `MatchSieve/`; run `node --check web/app.js`.
2. Inspect `git diff`/working tree if available. Never delete a failing test or silence exceptions to get a green build.
3. Confirm `.env.example` contains no live secret. Do not copy any `config/*_key.txt`, `.env`, Git history, SQLite database or private snapshots into a release archive.
4. Confirm the server binds to `127.0.0.1` by default and `/api/status` declares production readiness false.
5. Start a temporary local HTTP server with a disposable DB and drive the end-to-end route: status, fixture listing, market list, create fixture, research report, report history, report detail, browser assets and provider catalogue. Do not call live providers during baseline tests.
6. Report exactly what passes and fails before changing anything.

## Phase 1 — web customer path

Audit and test this path with an actual seeded fixture in a temporary DB:

1. First visit: honest server status and empty-fixture state.
2. Search fixtures and see stable competition/team/date information.
3. Select fixture, then market; prevent report submission without a fixture.
4. Generate once; show pending state and surface readable errors. No fake loading percentage or fabricated prediction.
5. Read summary/status, supporting signals, counter-signals, form/H2H only if present, missing facts and source snapshots/timestamps.
6. Open prior report from history and prove that the report ID and fixture ID are not confused.
7. Export/copy Markdown and verify the export includes source context and the limitations/method note.
8. Test narrow browser width, keyboard access, empty state, XSS-like team/source strings, network error and reduced-motion behavior.
9. Verify SportScore source attribution appears in all report outputs if required by selected provider terms—not just one visual surface.
10. Move manual fixture creation, CSV import, provider fetch and knowledge search to authenticated operator-only routes or keep them local-only. At present, this server has no auth and write routes are unsafe for public deployment.

## Phase 2 — API and backend correctness

- Confirm all routes in `docs/API_CONTRACT.md` map to real repository state; test malformed bodies, unsupported markets, invalid fixture/report IDs, empty histories, disabled providers, timeout errors and failed provider payloads.
- Review `Repository` SQL joins and report identity; test repeated report generation, source snapshot persistence, deduplication and SQLite transactions.
- The server is Python `http.server`/SQLite and is for local development. Before public deployment, migrate to a production WSGI/ASGI/server pattern or justify continued use with proper fronting, add request/rate limits, authentication/authorisation, CORS policy as needed, structured logging, database backups, schema migrations and health/readiness separation.
- Add evidence freshness rules and explicit `stale`/`unknown`/`not supplied` states. Missing values are not zeros. Preserve `LIMITED_EVIDENCE` on UI and API.
- Review market logic for denominator/sample-window correctness and add test cases. Do not tune thresholds to make historic results look better. Do not claim calibration/profitability without out-of-sample evaluation.

## Phase 3 — Android audit and wiring

From `MatchSieve-Mobile/`:

1. Open in Android Studio or use the checked-in Gradle wrapper if provided. Run unit tests, lint, debug build and release build; record exact environment/build outputs.
2. Verify package/application ID `com.matchsieve.mobile`, `MainActivity`, Compose, ViewModel, Retrofit, coroutine scopes and lifecycle behaviour.
3. Test the same real seeded backend: search fixture → select market → create report → see source/counter/missing data → open the same report from library.
4. Ensure report history rows use report IDs, unknown optional fields don't crash, null numbers are not rendered as zeros and `LIMITED_EVIDENCE` is visible.
5. Add tests for every snake_case model mapping, error JSON, null/stat fields, empty response and limited evidence.
6. Debug emulator URL may be `http://10.0.2.2:8765/`. Real phone on LAN requires the host machine's LAN address and trusted network; do not bind publicly for convenience. Release MUST use a real HTTPS API URL via `MATCHSIEVE_API_BASE_URL` / Gradle property. `https://api.example.invalid/` is a sentinel placeholder and is not usable.
7. Disable HTTP body/header logging in release. Keep provider keys and server secrets out of the APK; enforce permissions/paid entitlements on the server, not in Compose UI.
8. Make sure release shrinking doesn't break Retrofit/Gson serialization. Add required keep rules or an explicit serialization strategy and verify with a minified release build.
9. Add accessible loading/error/empty/retry states and verify on narrow screen, large text and network failure.

## Phase 4 — live integrations (only after provider/licensing choice)

- Do not choose the provider or fabricate its secret. Ask the project owner which licensed provider to activate once a candidate is confirmed.
- Keep all keys server-side. Start with one small request for one competition/date, record returned row count and schema, store capture time/source reference and check source terms/attribution.
- Add tests on sanitised recorded payloads, plus a short documented live smoke test. “A 200 was returned” is not enough.
- Implement cache/freshness/quota limits so opening the app/report does not create API calls on every tap.
- Confirm commercial display/redistribution rights for every customer-visible field and league before any paid launch.

## Phase 5 — paid account and release readiness (not yet built)

These are real gates, not items to mock as complete:

- Identify the legal selling entity, payment processor, currencies, taxes/VAT/sales tax, cancellation/refund and consumer disclosure requirements.
- Implement customer accounts, secure session handling, backend entitlements, subscription lifecycle, webhook signature verification, idempotency, refunds/cancellations, customer portal and failed-payment/grace-period behaviour.
- Enforce tenant/data access boundaries in server queries; prove one user cannot fetch another user's reports.
- Implement terms, privacy notice, data-retention/deletion policy, contact/support process, billing descriptors and incident procedure.
- Production HTTPS domain, secret storage, deployment pipeline, backups/restore rehearsal, logs/metrics/error reporting, uptime alerting, data/API cost budget and incident runbook.
- Web/mobile end-to-end test across install, signup, checkout, renewal state, cancelled/expired entitlements, report generation, logout and account deletion.
- Review marketing and outputs for jurisdiction-specific rules. The app is not a betting operator and must not promise winning bets/profit.

## Non-negotiable acceptance criteria before saying “ready”

1. Python tests, JS syntax test, Android unit tests, lint and debug/release builds pass in a documented supported toolchain.
2. One automated end-to-end test proves the shared web/mobile contract against a local seeded dataset without live calls.
3. A sanitized live smoke test proves the selected production provider works for declared league/date coverage, with rights/attribution approved.
4. Authentication, role controls, customer entitlements, billing webhooks and rate limiting are real and tested—not stubbed.
5. Release Android URL is HTTPS and no placeholder/secret is present in distributed artifacts.
6. Independent security review covers input validation, injection/XSS, request abuse, secret handling, dependencies and data isolation.
7. Backups/restore, logging, cost caps, incident ownership and terms/privacy are ready.

## Response expected from Codex

Return an audit table with `PASS / FAIL / NOT TESTED`, command evidence and file paths. Make the smallest high-confidence changes. For each remaining blocker, state why it is blocked and the exact operator input needed. Do not mark external credentials, legal rights, app-store review or production deployment “complete” based on local code alone.

## Phase 6 — consumer funnel wiring (new, design exists)

Read these files before implementing:
- `docs/UNIVERSAL_FUNNEL_MAP.md` — universal journey, offer ladder, region-routing policy, thank-you/payment states, community, platform-policy gates and automation choices.
- `web/funnel-preview.html` — interactive visual prototype of landing, opt-in, lead thank-you, offers, checkout and payment outcomes. It is deliberately front-end-only and must not be represented as live.
- `docs/COPY_BANK.md` and `docs/PAYING_CUSTOMER_PLAYBOOK.md` — approved claim boundaries and persona messaging.
- `docs/CONVERSION_EXPERIMENTS.md` — measurable validation plan.

Acceptance criteria:
1. The local GET route `/funnel-preview.html` serves only the design preview. Preserve the static asset allowlist; do not change it to unrestricted arbitrary file serving.
2. Convert the approved landing/opt-in/thank-you design into the real web app only after the project owner approves the visible page. Keep the core report workspace and funnel pages as clear separate routes.
3. Replace browser-only demo transitions with a real, validated lead-capture endpoint before any live use. Record legal basis/marketing consent separately, minimise stored data, add rate limiting, email validation, deduplication and deletion/retention rules. Add tests for invalid input, duplicate submit, consent states and delivery failure. Do not collect or send data from the preview page itself.
4. Use approved server-side product/plan configuration for prices and allowances. Do not hard-code a checkout amount in client code as the source of truth. The current £2.99 / £7.99 / £19 numbers are design hypotheses only.
5. Do not integrate Payhip, Gumroad, Stripe or another processor for the paid MatchSieve research product until the owner obtains written confirmation that the exact product, marketing and territory are accepted. These platforms publish restrictions relevant to gambling/sports forecasting; hiding the actual product function or mislabelling it is not an acceptable workaround.
6. Once approval is obtained, implement signed webhook verification, idempotency, correct payment/subscription state transitions, event audit, retries, refund/cancellation/chargeback handling, and server-side entitlements. A thank-you redirect must never grant paid access on its own.
7. Free community membership is optional and independent of payment. A paid Telegram invite must be issued only after verified active entitlement, should expire or be limited where practical, and must be revoked/re-evaluated when entitlement ends. Treat WhatsApp group links as shareable; app entitlement remains authoritative.
8. Country-specific prices/checkout must be an explicit, documented and tested pricing policy with final displayed currency, tax, renewal and cancellation details. Do not rely on IP geolocation alone to silently surprise customers. The UK is the first proposed pilot; other markets remain unapproved until billing, demand, tax and marketing reviews complete.
9. Add event definitions and consent-aware analytics only after privacy review. Never include personal data in UTM values, log payment data, or infer sensitive gambling vulnerability for advertising.
10. Add tests and report their exact local outputs. Do not claim the funnel is production-ready based on a static preview, an email provider connection or a successful browser redirect.

## Additional marketing integrity guardrail

Do not create or market an ebook titled “How to Bet Safely and Compound Daily.” The copy could imply betting is safe and that daily gains are expected. An educational resource can explain odds, uncertainty, variance, sample-size pitfalls, responsible limits and record-keeping without giving guaranteed outcomes or encouraging loss recovery. Prefer the product-aligned lead magnet “The 7-Point Match Research Checklist.”
