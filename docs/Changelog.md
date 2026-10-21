# Changelog

## 2026-10-21 — consumer messaging and validation foundation

- Expanded customer personas with psychographic hypotheses, buying triggers, objections, anti-personas, an interview script and a behaviour-based scorecard.
- Added the Paying-Customer Playbook covering positioning, value-first funnel stages, trust mechanisms, offer design, retention and ethical persuasion guardrails.
- Added a persona-specific Copy Bank, including homepage, Persona A/B/C, pricing placeholder, objection handling, lifecycle message and advertising copy.
- Added a Conversion Experiments register with event definitions, qualitative message-comprehension work and measurable headline, sample-report, segment, price, activation and publisher-workflow tests.
- Updated README navigation to expose the customer/conversion docs.
- Clarified the web workspace hero copy around the customer job and added a visible “Research a match” CTA to the existing research workflow.
- Fixed the legacy Form Engine contract: its returned result now includes the explicit evidence_available boolean already calculated by the engine.
- Removed the Evidence Engine's non-zero minimum confidence floor. A no-evidence report can now remain at confidence 0 instead of receiving a fabricated baseline of 5.

## Verification status

The local test output supplied on 21 October 2026 exposed a contract error in test_missing_form_is_unknown_and_not_counted_as_evidence: Form Engine returned no evidence_available key. Fixing that contract also surfaced the inappropriate minimum confidence floor in Evidence Engine, inconsistent with the test's expected zero-confidence result when there is no evidence. Both corrections are committed, but the test suite has **not** been rerun after these fixes in the user's VS Code environment. Run the required local commands after pulling.

The marketing experiment plan is specification only; no conversion experiment or price result has been measured.

## 2026-10-21 — universal funnel and monetisation design

- Added the universal funnel map for Persona A/B/C, including traffic attribution, opt-in and thank-you states, tripwire, core subscription, publisher upsell, retention, referrals, geographic routing and automation.
- Added explicit design-only price hypotheses for the UK test: £2.99 one-off pack, £7.99/month Researcher and £19/month future Publisher pilot. None are live prices or validated offers.
- Added the interactive funnel preview at web/funnel-preview.html. Its forms and checkout buttons only preview states in the browser; they do not send personal data, take payments or grant entitlements.
- Allowed the preview page through the local web server's static asset allowlist and added a route regression test.
- Documented Zapier Free and n8n deployment considerations, including the need for an always-on host for locally self-hosted n8n.
- Added a written-approval launch gate for the exact paid product category because Payhip, Gumroad and Stripe publish restrictions relevant to gambling/sports forecasting. Do not integrate live billing with those providers until the exact offer has been reviewed.
- Decision: UK-first controlled validation, organic/founder-led initially, with other markets on separately validated paths rather than silent IP-based pricing. No broad paid ad spend until product proof, data rights, market compliance and payment approval are resolved.

## Verification status

The previous local run in the supplied terminal log passed 38 tests after the earlier Form Engine and Evidence Engine corrections. The funnel route and new regression test were added after that reported run; they have not yet been executed locally. After pulling, rerun compileall, unittest discovery and node --check. The funnel preview is a visual prototype only and should not be exposed as a production sales funnel until real lead capture, consent, payment, entitlement and community integrations are implemented and tested.
