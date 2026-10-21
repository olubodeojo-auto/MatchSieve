# MatchSieve regional pricing and competitor research

**Status:** 21 October 2026. Public list prices observed online. User counts, paid subscribers and revenue are not verified unless a source discloses them. MatchSieve prices are experiments, not proven willingness-to-pay.

## Public competitor benchmarks

| Competitor | Published price observed | Interpretation | Verified user/revenue count |
|---|---|---|---|
| PIQSmart | GBP 7.50 first month then GBP 14.99/month; GBP 60 season offer | Premium prediction/selection product | Not disclosed on pricing page |
| Football Prediction AI | USD 9.99/month or USD 59.99/year | Subscription with prediction cards and accumulator tools | No user count disclosed; accuracy claim is provider-stated |
| Football Platform | UK GBP 0.99/week or 1.99/month; Nigeria NGN 1,900/week or 3,800/month; Ghana GHS 15/week or 30/month; Kenya KES 250/week or 500/month; Uganda UGX 4,800/week or 9,600/month; Eurozone EUR 1.19/week or 2.39/month; global USD 1.29/week or 2.59/month | Clear country-localised pricing benchmark | Not disclosed |
| MyPredictify | GBP 9.99/month; free tier includes credits | Credit-based access helps users experience value before upgrading | Not disclosed |
| SportsKinetic | GBP 9.99/month or 39.99/year | Trial-led subscription | Not disclosed |
| The Football Simulator | GBP 5.99/month or 39.99/year | Free layer plus deeper analytics | Not disclosed |
| Numbers Game | GBP 3.99/month Casual; GBP 12.99/month Analyst | Audience segmented by usage depth | Not disclosed |
| KOP AI | GBP 19.99/month Pro; GBP 29.99/month Elite; weekly options | Premium AI analysis and assistant | Not disclosed |
| eSureBet (Nigeria display) | NGN 2,000/3 days; 5,000/week; 16,000/month | VIP-tip benchmark, not a direct match to evidence-first research | Not disclosed |

## Regional persona hypotheses, not facts

- UK, US, Canada, UAE and selected EU: test the time-poor researcher and disciplined comparator. Message around reduced research effort, source transparency and counter-evidence; don't imply guaranteed betting advantage.
- Nigeria, Ghana, Kenya and Uganda: test small one-time packs and mobile payment completion. Do not assume every customer is price-sensitive; compare conversion, payment failures and repeat purchase by cohort.
- Frequent publishers/researchers: a future higher-volume offer may make sense only after interviews validate archive/export needs and repeat use.

The current product strategy identifies the UK as the first commercial test. Do not launch every country simultaneously. Pilot the UK first, then separately test Nigeria, Ghana and Kenya; evaluate other territories only after local payment, consumer-law, advertising and processor review.

## Test price policy currently represented in code

All are explicitly labelled pilot hypotheses:
- Nigeria: NGN 300 for 2 credits; NGN 700 for 6; NGN 500 for a matchday pass of 5 credits/24 hours.
- Ghana: GHS 2 / 5 / 4.
- Kenya: KES 20 / 50 / 40.
- Uganda: UGX 10 / 25 / 20.
- UK: GBP 0.79 / 1.99 / 1.49.
- US: USD 0.99 / 2.49 / 1.99.
- Canada: CAD 1.29 / 2.99 / 2.49.
- UAE: AED 3 / 7 / 5.
- Selected EU pilot countries: EUR 0.79 / 1.99 / 1.49.

These are not cleared for live checkout. Before activation, confirm provider acceptance of the exact product, transaction fees, taxes, refund/cancellation policy, country support and contribution margin. Unknown country codes fail closed. A matchday pass expires after 24 hours and includes a fixed credit allowance; it is not unlimited access.

## Event tracking and pricing decisions

Track report views, CTA clicks, checkout starts, completed purchases, repeat purchases, failed payments and credits spent. Segment by country, product, currency, experiment, campaign and persona path. Do not store card data, passwords, tokens or full IP addresses.

Core metrics:
- Report-to-CTA rate = unique CTA clickers / unique report viewers.
- Checkout completion = unique completed purchasers / unique checkout starters.
- Repeat purchase rate = purchasers with a later completed purchase / unique purchasers.
- Revenue per viewer = net revenue / unique report viewers.
- Contribution margin = net revenue less payment fees, provider/API costs, refunds and attributable infrastructure.

Change one variable per experiment and do not call a tiny sample a pricing verdict.

## Revenue scenarios: arithmetic, not forecast

At 1,000 qualified monthly visitors:
- 2% purchase conversion = 20 first purchases.
- At GBP 1.99 average order value, gross sales = GBP 39.80/month before fees, tax, refunds and data costs.
- At GBP 4.99 average order value, gross sales = GBP 99.80/month before costs.
- At 5% conversion and GBP 4.99 average order value, gross sales = GBP 249.50/month before costs.

Competitor sources:
- https://www.piqsmart.com/pricing
- https://www.footballprediction.ai/pricing
- https://footballplatform.com/become-a-member/
- https://mypredictify.com/pricing
- https://www.sportskinetic.ai/
- https://thefootballsimulator.com/pricing
- https://numbersgame.uk/signup
- https://kop-ai.com/en/pricing
- https://esurebet.com/pricing

Competitor pricing pages generally do not disclose reliable active users, paid subscriber counts or audited revenue. Do not invent these numbers; use filings, credible interviews or independently sourced traffic estimates and label what each metric measures.
