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
