# MatchSieve Conversion Experiments

**Status:** Proposed test plan. No experiments or conversion lift have been measured yet.  
**Primary goal:** Discover which users repeatedly value MatchSieve enough to pay, while keeping evidence quality and honest marketing intact.  
**Do not buy traffic yet:** validate the actual report, source permissions, payment path and unit costs first.

## 1. Funnel events and definitions

Use consistent event names so web and Android can eventually measure the same journey. Do not collect personal details in analytics payloads unless strictly necessary and covered by the privacy plan.

| Event | Definition | Important fields (minimum) |
|---|---|---|
| landing_view | Product landing page loaded | source/campaign if consented |
| sample_report_opened | Sample report opened | sample version |
| research_started | User begins creating a report | client, market code |
| fixture_selected | A stored fixture selected | competition code where appropriate |
| market_selected | A market is selected | market code |
| research_completed | A report is returned and rendered | status, duration bucket |
| report_inspected | User opens source or detail sections | section type only |
| report_saved | Report successfully saved | report status |
| report_exported | Export completes | export type |
| checkout_started | User opens a plan checkout | plan ID, displayed price |
| subscription_paid | Payment provider confirms first payment | plan ID, currency; never card data |
| subscription_cancelled | Cancellation is confirmed | optional reason category |
| payment_refunded | Refund is confirmed | amount/currency |
| research_returned_7d | User completes another report within 7 days | cohort and count only |

The event list is a specification, not a claim that the events are currently implemented. Define a privacy and consent policy before adding analytics. Avoid collecting report text, API keys, payment details or unnecessary user identifiers. Do not infer a person's gambling habits or financial stress for ad targeting.

## 2. North-star and guardrails

**North-star:** paid customers who complete useful research, return in a later week and produce positive contribution margin.

Supporting measures:
- Landing → sample report open.
- Sample report → research started.
- Research started → report completed.
- Report completed → source/details inspected.
- First report → second report in 7 days.
- Qualified visitor → completed paid checkout.
- First payment → second billing period.
- Reports per paid subscriber and provider cost per report.
- Refunds, complaints, support load and cancellation reasons.
- Share of reports limited by missing/stale evidence; this is a product-quality measure, not automatically a negative.

Do not maximise paid conversion at the expense of comprehension, honest expectations or cancellation access. A high initial conversion rate paired with refunds, poor usage or rapid churn is a failed experiment.

## 3. Experiment sequence

### Experiment 0 — Qualitative message comprehension
**Question:** After seeing the value proposition and a real sample, can target users explain what they would pay for and what the product does not promise?

- **Audience:** 8–12 adults who actually research football matches, with both Persona A and C represented; include several sceptical Persona B users.
- **Method:** moderated task, not a leading sales pitch. Show the page for 5 seconds; ask them to explain the product in their own words. Then let them use the sample and think aloud.
- **Observe:** whether they understand fixture + market specificity, source trail, counter-evidence and missing-data honesty; what they confuse with free livescores or guaranteed picks.
- **Pass signal:** a clear majority can describe the paid difference without prompting, and users can identify at least one useful element in the report. Treat a small interview sample as directional only.
- **Failure response:** revise clarity before buying traffic or arguing that users “don't get it”.

### Experiment 1 — Headline framing
**Hypothesis:** the explicit workflow headline will generate more qualified sample opens than the abstract category tagline.

- **A (control):** “Football research. Without the noise.”
- **B (variant):** “One match. One market question. The evidence in one place.”
- **Keep constant:** subheadline, page structure, report sample, CTA, audience and period.
- **Primary measure:** sample-report opens per eligible landing visitor.
- **Guardrails:** bounce/exit, research-start rate, misunderstanding during brief user interviews.
- **Decision:** choose B only if it improves qualified engagement without increasing the share of visitors who think MatchSieve guarantees a result. With low traffic, use the result as a directional signal and repeat; do not declare statistical certainty from a handful of visitors.

### Experiment 2 — Show the mechanism, not a feature grid
**Hypothesis:** an annotated real sample showing support, counter-evidence, sources and missing information will produce more research starts than generic feature cards.

- **A:** three short capability cards.
- **B:** one reviewed report excerpt with its date, data window, source trail and a visible limitation.
- **Primary measure:** research starts after sample viewing.
- **Guardrails:** report comprehension, expectation accuracy and page performance.
- **Important:** all data must be permitted and real for the stated match. Clearly label an illustrative/synthetic example; never pass it off as real data.

### Experiment 3 — Persona A versus Persona C message
**Hypothesis:** the publisher's repeated deadline and source-attribution job may create a stronger repeat-use case than general researcher messaging.

- **A page:** “Stop guessing the odds. Examine the evidence.” CTA: “Explore a reviewed sample report”.
- **C page:** “Research the match. Keep the sources. Make the argument yours.” CTA: “Review a sample research brief”.
- **Audience:** adult visitors recruited for the stated job, not simply broad football-interest clicks.
- **Primary measure:** qualified research starts and return within 7 days.
- **Secondary measures:** whether publishers need export, multiple fixtures, source citation and commercial redistribution rights.
- **Decision:** if C shows stronger repeated use, build the smallest validated publisher workflow before a separate creator plan. Do not infer product-market fit from one enthusiastic creator.

### Experiment 4 — Premium £19/month UK pilot
**Prerequisites:** a reviewed real sample report, defined supported competition set, actual subscription/entitlement service, functioning and approved payment account, clear limits, support/refund route and working cancellation path. Before these exist, use interviews and non-binding interest forms only; call them leads, not sales.

- **Offer:** one UK Research Desk membership at £19/month, with a proposed limit of up to 20 full research briefs per billing month. No cheaper trial pack, matchday pass or hidden discount at launch.
- **Audience:** adult UK visitors who match the serious independent researcher or show a real repeat research/publishing job.
- **Primary measures:** completed paid checkout per qualified visitor, first report completion, second report use and first renewal.
- **Guardrails:** payment failure, refunds, early cancellation, complaints, support load and contribution margin after processing, tax, data and attributable infrastructure costs.
- **Decision:** do not interpret clicks, wait-list sign-ups or praise as willingness-to-pay. Keep the offer only if real purchases, use and repeat behaviour support the unit economics. If it underperforms, examine audience fit, product proof, source coverage and checkout before reflexively lowering price.

### Experiment 5 — Repeat-use and allowance fit (no economy tier)
**Question:** does the proposed 20-brief monthly allowance fit the recurring job of the premium customer?

- **Prerequisite:** usage must be measured on a functioning product; do not promise the allowance before it is enforced.
- **Measure:** reports started/completed, repeated cross-checking avoided as described by users, proportion of members approaching the allowance, renewals, cancellations and cost-to-serve.
- **Segment:** serious independent researchers first; publishers are interviewed separately and are not promised a publisher tier.
- **Decision:** refine the premium allowance only when actual usage and costs justify it. Do not add credits or a low-cost offer just to capture unqualified price shoppers.

### Experiment 6 — First-use activation
**Hypothesis:** a short, guided first run with a sample report and plain-language market descriptions will improve first-report completion without hiding uncertainty.

- **A:** enter the workspace and choose the fixture.
- **B:** guided sequence: select a sample/stored fixture → choose a market → inspect the report structure.
- **Primary measure:** research completion among people who start.
- **Guardrails:** time to completion, error rate, unsupported interpretations and whether the user notices a LIMITED_EVIDENCE status.
- **Decision:** adopt the guided path if it improves completion and comprehension, not simply clicks.

### Experiment 7 — Publisher workflow proof
**Hypothesis:** repeatable source-preserving export and multi-fixture research can support a distinct publisher offer.

- **Test:** ask publishers to complete a preview from a real, reviewed report; observe source checking, rewriting, citation, and time taken.
- **Measure:** repeated usage across a later publishing deadline, willingness to pay for the exact working feature, and permission/licensing requirements.
- **Do not build:** a large publishing suite based solely on interview enthusiasm. Start with the smallest feature repeatedly requested and permitted by source licences.

## 4. Method for small samples

- Define one hypothesis, one main measure and no more than two guardrails before every test.
- Do not change headline, price, page layout and sample report in the same experiment.
- Record start/end dates, audience source, eligible visits, action counts, complaints, refunds and interpretation.
- If the sample is small, report raw counts and uncertainty. Repeat or interview users; do not call a difference “proven”.
- Keep a result only if it improves qualified use and does not worsen trust, user comprehension, evidence quality or retention.
- Stop an experiment immediately if copy is misunderstood as a guarantee or users report pressure or misleading pricing.

## 5. A first 30-day validation sequence

**Week 1:** interview 8–12 target adults; show a reviewed sample; update this file with verbatim objections and anonymised findings.  
**Week 2:** fix the greatest report-comprehension issue; prepare two honest message variants; ensure sample data licensing and timestamps are clear.  
**Week 3:** run a small controlled landing/message test; measure qualified report starts and successful report completion.  
**Week 4:** if first-use quality is acceptable and payments are ready, run a small paid pilot with explicit terms; follow cohort usage and ask for a renewal decision after real value was delivered.

If payment integration is not ready, finish the research and activation tests. Do not simulate sales or report interest form submissions as revenue.

## 6. Launch and scale gates

Do not scale paid acquisition until:
- provider/data display rights and coverage are checked for the actual competitions shown;
- the sample report is real, permitted, reviewed and transparent about gaps;
- authentication, rate limits, user report ownership and payment entitlements protect the backend;
- price, usage limit, renewal, cancellation and refund information is clear;
- customers can complete research and return without help;
- retention, cost-to-serve and contribution margin support the plan;
- UK marketing has been reviewed for betting-adjacent claims, and each later territory has a separate compliance review.
