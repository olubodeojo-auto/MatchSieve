# Changelog

## 2026-10-21 — consumer messaging and validation foundation

- Expanded customer personas with psychographic hypotheses, buying triggers, objections, anti-personas, an interview script and a behaviour-based scorecard.
- Added the Paying-Customer Playbook covering positioning, value-first funnel stages, trust mechanisms, offer design, retention and ethical persuasion guardrails.
- Added a persona-specific Copy Bank, including homepage, Persona A/B/C, pricing placeholder, objection handling, lifecycle message and advertising copy.
- Added a Conversion Experiments register with event definitions, qualitative message-comprehension work and measurable headline, sample-report, segment, price, activation and publisher-workflow tests.
- Updated README navigation to expose the customer/conversion docs.
- Clarified the web workspace hero copy around the customer job and added a visible “Research a match” CTA to the existing research workflow.
- Fixed the legacy Form Engine contract: its returned result now includes the explicit evidence_available boolean already calculated by the engine. This addresses the missing key reported by the local unittest run.
- No claims of production readiness are added. All marketing/pricing ideas remain hypotheses until tested with real target users and observed purchase/retention behaviour.

## Verification status

The local test output supplied on 21 October 2026 showed one error in test_missing_form_is_unknown_and_not_counted_as_evidence: Form Engine returned no evidence_available key. The code fix is committed, but the test suite has **not** been rerun after the fix in the user's VS Code environment. Run the required local commands after pulling. The marketing experiment plan is specification only; no conversion experiment or price result has been measured.
