# MatchSieve Web Customer Journey

## Product promise

Help a time-poor football researcher move from a fixture and an explicit market question to a useful, source-traceable evidence brief. Do not imply that MatchSieve runs a sportsbook or guarantees profitable bets.

## Journey A — first visit

1. **Orient:** the header and hero identify MatchSieve as football research, not a score-only service. A status strip tells the user whether the local archive has fixtures/reports and whether the backend is reachable.
2. **Find a fixture:** search by club, competition or text already present in the archive. The default list is bounded. If no records are found, explain that this installation has no matching fixtures yet and direct an operator to import a permitted CSV or enable one reviewed provider. Do not silently fabricate fixtures.
3. **Choose a research question:** choose the requested market before generating a report. Market names should use ordinary language and the market code should be retained in the report.
4. **Generate:** show real loading state, block accidental duplicate submissions and report backend/network errors in plain language. The animation, if any, is decorative; it must never imply a probability or model confidence that has not been calculated.
5. **Interpret the brief:** identify the fixture and market; put the evidence status close to the top; separate supporting signals from counter-signals; show sample sizes/team form only where stored data supports them; show missing data clearly; list source references and capture times; show the method disclaimer.
6. **Keep/reuse:** persist the report locally, offer report history, open a saved report without recalculating it, and allow Markdown export/copy.

## Journey B — returning researcher

1. Open report history.
2. Scan report identity (fixture, market, time, status).
3. Open a prior report using the report ID endpoint.
4. Make clear that a saved report is a snapshot of its inputs at generation time; it is not a live view and should not be represented as current if its evidence has aged.
5. To refresh, the researcher deliberately runs a new report after refreshing the underlying data.

## Journey C — empty or weak data

- Empty fixture archive: honest empty state, not a fake sample list.
- Unknown fixture ID: not-found message.
- Sparse historical records: `LIMITED_EVIDENCE`, explicit missing-data list and no invented percentages.
- Failed provider call: show provider error and the fact the import failed; do not display an empty success state.
- Report creation failure: preserve fixture/market selection so the user can retry.
- Stale data: the current foundation preserves source capture metadata, but freshness policy/thresholds have not yet been implemented. Codex must add and test explicit stale-data flags before launch.

## Operator area

The local UI includes manual fixture creation, CSV import, provider catalogue/fetch and knowledge search. They are labelled as operator/development controls and should not be exposed to anonymous SaaS visitors. Current foundation has no administrator authentication; Codex must move these routes behind an authenticated operator role or remove them from the public app and backend before any public deployment.

## Accessibility/responsiveness

Keep controls labelled, keyboard navigable and visible at desktop/mobile widths. Status must not rely on colour alone. Support reduced motion. Empty/loading/error/success states are required. Avoid huge unfiltered lists and avoid representing non-linked data as fact.

## Acceptance criteria for the web flow

- A fixture can be selected, a market selected and a report generated end-to-end from seeded local data.
- The report shows source provenance, supporting and counter evidence, missing information and status.
- History and report detail endpoints return the same report identity and market.
- The interface truthfully handles empty archives, errors and `LIMITED_EVIDENCE`.
- No public anonymous access to fixture writes, imports, provider fetch, internal knowledge search or reports containing data outside the user's access scope.
- No claims of production readiness until identity, authorisation, billing entitlements, provider rights, public hosting, backups, monitoring and end-to-end tests are complete.
