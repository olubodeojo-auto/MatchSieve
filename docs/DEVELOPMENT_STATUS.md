# Development Status — MatchSieve v0.3.0

## Verified in the current workspace

- Backend Python source compilation passes.
- Automated suite currently has **24 offline Python tests** covering report calculation, ingestion, provider payload mapping and mobile API contract mapping. Re-run before release.
- `node --check web/app.js` passes.
- Local HTTP smoke test against temporary SQLite proved `/api/status`, `/api/mobile/fixtures`, `/api/mobile/markets`, `/api/mobile/research/history`, `/api/providers`, `/`, `/app.js`, `/style.css`, manual fixture creation, report generation, report history and report detail. No live provider was called.
- Android source has typed Retrofit models/client, ViewModel and Compose fixture→market→research→saved-report flow. Two Gson mapping unit tests have been added. **They have not been executed** because this environment lacks Gradle and Android SDK.

## Not verified / launch blockers

- Live provider coverage, response schema, pricing/quotas or commercial use rights for any selected launch competitions.
- Fresh upcoming fixture feed, injuries, suspensions, line-ups, odds or xG across launch competitions.
- Android Gradle compile, Android unit test execution, lint, emulator/device flow or minified release APK.
- Customer accounts, authentication/authorisation, report ownership, subscription billing, webhooks or server-side entitlements.
- Public deployment, real HTTPS API URL, rate limiting, monitoring, backup/restore and production security review.
- Data freshness thresholds and stale-data status, legal pages and operational support.
- Any calibrated prediction accuracy or betting-profit claim.

The accurate status is **populated, locally testable foundation with the main report workflow and mobile API wiring implemented**. It is not a production deployment. See `PROJECT_STATUS.md`, `INTEGRATION_READINESS.md` and top-level `CODEX_HANDOFF.md` for the concrete next steps.
