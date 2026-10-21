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


## Additional country-level competitor evidence checked on 21 October 2026

These are public claims and published prices. A competitor's own member count is not an audited active-user metric.

| Country / market | Competitor evidence found | Implication for MatchSieve |
|---|---|---|
| Nigeria | KiqStat advertises NGN 5,000/month for Pro. eSureBet displays NGN 2,000/3 days, NGN 5,000/week and NGN 16,000/month. EC Predicts claims 12,000+ members and lists premium tiers, but its displayed pricing is high relative to a low-cost research tripwire. Pokotips claims 3,500+ subscribers and lists NGN 3,499/month. | A tiny one-time report pack could reduce commitment versus subscriptions, but ₦300 must be judged against processor fees and report-generation cost. |
| Ghana | StatPulse AI lists GH₵70/7 days, GH₵200/30 days, GH₵400 Pro and GH₵1,000 Verdict. NOVA247 lists GHS 120, 250 and 450/month. Football Platform lists GH₵15/week or GH₵30/month. | Market pricing varies sharply by positioning; a small credit pack is a different value proposition from VIP tips. Do not benchmark only against the highest tier. |
| Kenya | Sokastar lists KES 250 for a daily package and KES 50/40/80 for selected daily products. WekaTips lists KES 70 for one day, KES 150 for seven days, and SMS products from KES 50/day. Football Platform lists KES 250/week and KES 500/month. | Daily access is an established packaging pattern. A KES 20 two-credit pack is a lower-priced experiment, not proven demand. |
| Uganda | Football Platform lists UGX 4,800/week and UGX 9,600/month. No second strong, transparently priced local competitor was verified in this pass. | Treat Uganda as a later small cohort; test payment method success and repeat behaviour before expanding. |
| US / Canada | Football Prediction AI publishes USD 9.99/month or USD 59.99/year. It is a global offer, not a verified country-local benchmark. No strong Canada-specific price and subscriber count were verified in this pass. | Use local currency and a separately measured cohort. Do not assume USD pricing translates directly into Canadian willingness to pay. |
| UAE / Dubai | No strong UAE-specific competitor with transparent local pricing and credible audience figures was verified in this pass. | Do not infer UAE willingness to pay from UK or US prices; test only after payment and marketing review. |
| UK / EU | PIQSmart publishes GBP 7.50 first month then GBP 14.99/month and a GBP 60 season offer; Football Platform publishes GBP 0.99/week or GBP 1.99/month; SportsKinetic publishes GBP 9.99/month or GBP 39.99/year. Football Platform lists selected Eurozone prices. | There is a broad price range. Our entry product should sell a clearly bounded research outcome, not claim to match a full prediction subscription. |

### Audience size and revenue claims

- EC Predicts publicly claims 12,000+ members; Pokotips publicly claims 3,500+ subscribers. These are self-reported marketing claims, not independently verified monthly active users or paid subscribers.
- The other pricing pages reviewed did not disclose credible paid-user counts or audited revenue. No traffic estimate is substituted for paying users.
- A reliable competitor-revenue estimate cannot be derived from list price multiplied by a claimed audience because plan mix, churn, discounts, free accounts and payment success are unknown.

### Updated sources

- KiqStat: https://www.kiqstat.app/
- EC Predicts: https://ecpredicts.com/
- Pokotips: https://pokotips.com/membership/registration
- StatPulse AI: https://statpulseai.com/
- NOVA247 Tech: https://nova247.tech/pricing
- Sokastar: https://sokastar.com/
- WekaTips: https://www.wekatips.co.ke/
- Sportverified: https://www.sportverified.com/pricing.php
- Football Platform: https://footballplatform.com/become-a-member/
- Football Prediction AI: https://www.footballprediction.ai/pricing
