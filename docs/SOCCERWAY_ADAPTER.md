# Soccerway Collection Adapter — Engineering Standard

## Purpose and authority

matchsieve.collectors.soccerway.SoccerwayAdapter is the source-specific adapter for collecting one Soccerway match and its available tabs. It is designed to produce structured, source-traceable evidence and a raw snapshot for the local knowledge base. It does not recommend a betting market, certify a result, or make missing values up.

The adapter is a collection component, not a guarantee that Soccerway publishes every metric for every fixture. Team sheets, xG, possession, cards, events and detailed statistics may be absent or differ by competition/match. Every returned field is source-reported and must remain distinguishable from a MatchSieve-derived calculation.

## Daily match-list to selected fixture

The expected journey is: date/matches page → list all available fixtures for that date → researcher selects one fixture → match overview → research tabs → historical evidence. The new command supports collecting a date/list URL and printing an indexed, reviewable fixture list. A selected index is only a convenience for the current captured order; the stable match URL is the true identifier and should be saved/used after selection. The matcher must not silently assume the first match is the intended fixture.

A daily-list capture is separate from detail-page capture. The list adapter stores the raw list snapshot, competition/fixture rows, visible kickoff and score/status where explicitly displayed, and each fixture's actual source link. It must not guess missing team names from unrelated page text.

## Explicit page discovery

The collection workflow has two entry points. First, it can start from a Soccerway daily matches page, extract the visible fixture list grouped by competition where the page provides that structure, and archive the fixture links. Second, the researcher selects one fixture and the match adapter checks that fixture identity before visiting its research tabs. It looks for these logical page types, in this order:

1. Match overview
2. Report
3. Odds
4. Head-to-head (H2H)
5. Standings
6. Match statistics
7. Line-ups
8. Player statistics
9. Commentary / events

It first inspects links on the supplied match page and classifies those links by label/path. It then tries known same-match route patterns for tabs not found by link discovery, subject to a hard page limit. The current first version's route fallbacks are candidate routes only and need validation against current Soccerway pages; use the actual tabs discovered from the page whenever possible. This is a discovery strategy, not a promise that every route exists. A route returning an error or a tab containing no relevant data remains unavailable; it is never filled from assumptions.

## Explicit extraction layers

The adapter uses an ordered, inspectable extraction process:

1. **JSON-LD:** inspect embedded structured event metadata when present.
2. **Named DOM selector groups:** capture candidates for home team, away team, team names, score, kick-off/date, competition and venue. The saved candidate includes the selector that found it.
3. **Page title and headings:** parse a Home v Away pair when it is explicit in the title/heading.
4. **Table rows:** preserve table cells and parse only recognized statistic labels with distinct explicit home and away values, including a middle-label or edge-label layout where the two side values are explicit.
5. **Player links:** collect visible player names and same-site URLs from line-up/player-stat/overview pages.
6. **Minute-stamped events:** extract plausible goal, card and substitution rows from event-like elements; retain raw text because the classification is a heuristic.
7. **Visible text and raw snapshot:** retain the page text for later audit, capped to a safe size.

### H2H and historical form

The intended research capture for the H2H tab is broader than one visible list. The adapter separately targets home-team recent matches, away-team recent matches, and direct H2H meetings. It tries up to four expansion clicks per clearly identified section and stores rows only under a section whose heading/container is distinguishable; otherwise rows stay under `unassigned_visible_history_rows`. Target counts are up to 30 recent matches for each team and up to 15 direct meetings, where the source exposes them. The target counts are not a promise: the extracted row count and headings must be checked, and absent games must never be invented.

On the Stats tab, the collector attempts explicit first-half and second-half controls (where present) and stores those captures separately as `statistics_by_period.full_match`, `first_half` and `second_half`. If the controls do not exist, the resulting warning is evidence of a source limitation, not a reason to scrape around access controls.

The structured extraction is intentionally conservative. A value without an identifiable selector or source context must not be called verified. Score parsing permits a genuine zero score; missing fields are checked against None/empty values, not truthiness. Kick-off values retain their original representation and are **not silently relabelled UTC** when the page's time zone is unknown.

## Evidence archive and running it

Install Playwright and its Chromium browser once from the MatchSieve repository root:

~~~powershell
python -m pip install playwright
python -m playwright install chromium
~~~

First capture the day's list, then collect the selected fixture:

~~~powershell
python scripts/collect_soccerway.py --date-url "https://ng.soccerway.com/"
python scripts/collect_soccerway.py --date-url "PASTE-ACTUAL-DAY-URL"
python scripts/collect_soccerway.py --match-url "https://ng.soccerway.com/match/home-team-id/away-team-id/"
~~~

The date/list command saves and prints the visible fixture URLs in page order; use a fixture's actual URL as the stable selection. `--match-index N` can collect the Nth fixture from a newly captured list, but an index is not a stable identifier across changed list ordering. Date-list extraction is still DOM-sensitive and must be checked against the visible list before production use.

The script writes dated JSON under knowledge-base/source-snapshots/soccerway/. The report contains captured page tabs, extracted fields, source URLs, capture times, warnings and gaps. Review the JSON before relying on the extraction.

To review the archived evidence with the specialist-agent runner:

~~~powershell
python scripts/run_agent_pipeline.py "knowledge-base/source-snapshots/soccerway/ACTUAL-FILENAME.json" --market OVER_UNDER_MATCH_GOALS
~~~

Replace the placeholder with the actual printed filename. The runner is an isolated review tool at present; the existing matchsieve/reporting.py::generate_report path is still the main application reporting flow. The specialist pipeline has **not** been integrated into the live report-generation path by this adapter-only change.

## Stop conditions and responsible use

- Accept only Soccerway hosts and match/game routes.
- Keep requests on the caller-supplied locale host and the same match.
- Use a page limit and delay between tab requests.
- Stop immediately on HTTP 403/429 or an obvious access challenge. Do not retry around a block.
- Do not bypass logins, paywalls, CAPTCHA, bot controls or other restrictions.
- Retain source URLs, capture time, HTTP status, page type, extraction selectors, raw text/tables, errors, warnings and missing fields.
- Check Soccerway's applicable terms, robots guidance and data-use rights before any commercial use. Public visibility is not permission to republish or commercially redistribute provider data.
- Never fabricate xG, line-ups, possession, scores, events or injuries when absent.
- Do not market the collector as live until freshness, runtime and source availability are measured and enforced.

## Current acceptance checklist

- [x] Source-specific adapter module and export
- [x] Date/list entry point and structured fixture-link extraction added
- [x] Same-match tab discovery plus known route fallbacks
- [x] Explicit selector groups with selector provenance for common match fields
- [x] Bounded visible-history expansion helper added to H2H path
- [x] Table-based stat candidates, player links, minute-stamped event candidates and JSON-LD
- [x] Missing-field and access-block reporting; raw snapshot archive CLI
- [x] Offline unit tests authored for URL validation, discovery, title parsing, stat parsing and bounds
- [ ] Run the offline tests in VS Code
- [ ] Compare output against representative current Soccerway date list and overview, stats, H2H, line-up and commentary pages, where those tabs are available
- [ ] Make list extraction section-aware so competition, kickoff, teams and match URLs remain correctly grouped
- [x] Separate storage keys for each team’s recent matches, direct H2H meetings and first-/second-half statistic captures when explicit controls exist
- [ ] Validate that extracted row counts/section boundaries match representative current pages; targets are up to 30 per team and up to 15 direct meetings, only when shown by source
- [ ] Replace generic expansion classification with section-aware controls and verify expansion counts against visible source rows
- [ ] Add reviewed selector fixtures captured in accordance with source terms; test confirmed zero-score, date/time-zone, alternate table and absent-stat cases
- [ ] Verify commercial-use rights/data licensing before paid publication
- [ ] Integrate archived records and the agent pipeline into the existing report repository without discarding the legacy evidence calculations

This is a structured first version, not a claim that all current live Soccerway DOM variants have been validated. Current site layouts can change, so a controlled fixture set and the offline tests are required before relying on it for paid reports.
