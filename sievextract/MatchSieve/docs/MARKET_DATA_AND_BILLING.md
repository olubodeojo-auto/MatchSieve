# Market data, international billing and launch economics

**Checked:** 20 October 2026. Prices and onboarding rules can change; confirm terms with the provider before paying or registering an entity.

## 1. Product strategy

MatchSieve is a paid research workflow, not a general-purpose live-score clone. Use a licensed fixture/score feed as an input. The paid difference is market-specific analysis: relevant recent results, home/away splits, head-to-head only when useful, counter-signals, missing/stale data, capture timestamps and links/provenance. Do not represent a descriptive report as a calibrated probability or guaranteed betting outcome.

### Data-feed shortlist

| Provider | Published entry tier checked | Fit / caveat | Source |
|---|---:|---|---|
| football-data.org | €12/month for “Free w/ Livescores” | 12 competitions, live scores, fixtures, schedules and tables. Check competition coverage and display/redistribution terms. | https://www.football-data.org/pricing |
| API-Football | $19/month Pro | 7,500 requests/day; its pricing page lists livescore, fixtures, events, lineups, H2H and multiple statistics endpoints. Check endpoint-specific coverage and use rights. | https://www.api-football.com/pricing |
| Sportmonks | €29/month Starter | 5 selected leagues; livescores, fixtures, events and lineups, with published higher tiers at €99 / €249 / from €499 monthly. | https://www.sportmonks.com/football-api/solutions/live-score-api/ |
| Stats Perform / Opta | Quote-based | Enterprise option to revisit when coverage, SLAs and rights justify a negotiated licence. | https://www.statsperform.com/faqs/stats-perform-faqs-pricing-licensing/ |

**Recommended validation:** test API-Football against football-data.org for the exact first release leagues. Start with the Premier League plus only the next competitions justified by customer research. Log feed latency, missing fixtures, postponed games, corrections, response quotas and raw provider timestamps. Do not redistribute raw provider data or cache it beyond contract terms without permission. Never make a commercial product dependent on scraping SofaScore, Soccer24, LiveScore or another data app.

Manual fixtures and historical CSVs are acceptable to demonstrate the research workflow while funding is tight, but they are not a defensible real-time data pipeline. Keep manual data labelled and time-stamped.

## 2. Billing routes for a Nigeria-based founder

The current Stripe global availability page lists Nigeria under **Extended network** and links it to Paystack, whereas the UK, US, Canada and Australia are listed as standard supported markets: https://stripe.com/global. Paystack documents recurring charges and, for Nigerian accounts, accepting international card payments; its country/currency table lists Nigerian collection currencies as **NGN and USD**, not GBP or EUR. Sources: https://paystack.com/docs/payments/subscriptions/ and https://support.paystack.com/en/articles/2130690.

### Route A — validate from Nigeria first

Use a Nigerian Paystack account to validate willingness to pay, possibly with USD pricing if the relevant account is approved for international payments. This avoids incorporating a foreign company before product-market fit. It does **not** meet the exact “charge subscriptions in GBP or EUR” requirement, and Paystack's fees and settlement currency must be included in the model.

### Route B — UK private limited company, potentially the lowest raw-fee foreign-company path

Stripe's own cross-country onboarding guidance says opening an account in a country other than the primary business country requires a legal entity, tax ID, physical location, phone number, government ID, working website and a physical bank account in the country. A company certificate alone is insufficient: https://support.stripe.com/questions/requirements-to-open-a-stripe-account-in-another-country?locale=en-GB.

- Companies House's digital incorporation fee is £100 from 1 February 2026: https://www.gov.uk/government/news/companies-house-fees-are-changing-from-1-february-2026.
- The online confirmation-statement filing fee is £50: https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees.
- The company needs an appropriate physical UK registered-office address and a contact email. A paid agent/accountant address may be possible if it meets the statutory requirements and the provider consents: https://www.gov.uk/limited-company-formation/company-address.
- Annual accounts, confirmation statements, tax filings and bookkeeping continue after incorporation. The statutory formation fee is not the full cost of operating the company. Budget separately for the registered office, accounts/tax service, banking, exchange costs and advice.
- UK corporation tax is 19% on profits under the £50,000 small-profits limit and 25% above £250,000, subject to eligibility and marginal relief between the limits: https://www.gov.uk/government/publications/rates-and-allowances-corporation-tax/rates-and-allowances-corporation-tax.
- Because the founder and day-to-day work are in Nigeria, obtain cross-border tax advice before choosing this route. The UK–Nigeria double-taxation agreement exists, but it does not automatically remove reporting obligations in either country: https://www.gov.uk/government/publications/nigeria-tax-treaties/1987-uk-nigeria-double-taxation-agreement-in-force.
- A third-party non-resident formation package currently advertises £129.99 plus the £100 Companies House fee, including a first-year registered office, director service address and identity-check support; this is a vendor's offer, not an endorsement or a guarantee of Stripe approval: https://www.theformationcompany.co.uk/international-package.
- **Planning budget:** allow roughly £500–£1,000 for a first year of a trading, single-director UK Ltd once formation, appropriate address services, the £50 annual confirmation statement and basic accounts/tax service are included. This is a planning range, not a quote; banking, tax advice, VAT registrations, mail handling and complex filings can add more.
- Incorporation is not a promise that Stripe will approve a particular account. Before paying a formation agent, ask Stripe to confirm the documentation and physical-location/banking requirements for a UK company owned and operated by a Nigeria-resident founder. Give true ownership, residential address, operating location and banking information; do not use a mailbox as a fictional operating base.

### Route C — Stripe Atlas / Delaware company

Stripe Atlas publishes a $500 one-time setup fee including incorporation, tax ID and first-year registered-agent service, with $100/year for the agent after year one: https://stripe.com/atlas. This is a route designed for founders outside the US, but it is not the cheapest headline setup. Atlas companies have annual US federal/state filing obligations and Delaware fees/taxes; Stripe's own guidance recommends a tax professional: https://support.stripe.com/questions/legal-and-tax-help-for-your-stripe-atlas-company?locale=en-GB. Get a tax quote before selecting LLC vs C-corporation. Do not assume that a company formation package removes US or Nigerian tax responsibilities.

### Not preferred without a specific reason

- **Australia:** official registration fee is AUD 636 from 1 July 2026, and Australian companies generally need at least one director ordinarily resident in Australia. Not a low-friction choice without such a director. Sources: https://business.gov.au/news/changes-for-businesses-from-1-july-2026 and https://www.asic.gov.au/for-business-and-companies/companies/company-building-blocks/company-officeholders-directors-and-secretaries.
- **Canada:** do not incorporate there only to unlock a payment processor; compare ongoing filings, address/banking needs and tax treatment first.

**Practical recommendation:** UK Ltd is cheapest on its statutory fee alone, but may not be cheapest to make *usable* for Stripe if the physical address and bank requirements cannot be met. Stripe Atlas is the more explicit remote-founder setup route at $500 upfront and $100/year for the registered agent after year one, but it brings US tax/accounting costs. Before committing, ask Stripe to confirm in writing which path they will accept for a founder living and operating from Nigeria. If that answer is not clear, do not spend money on foreign incorporation just to try a payment processor. If cash is extremely tight, validate willingness to pay through a Nigerian USD-capable collection path first, knowing it will not meet the exact GBP/EUR currency preference.

## 3. Stripe fees and price point

Stripe UK's published standard online card pricing is 1.5% + 20p for standard UK cards, 2.5% + 20p for EEA cards, and 3.15% + 20p for international cards; a 2% currency conversion fee may apply when conversion is needed. Stripe Billing's pay-as-you-go price is 0.7% of Billing volume. Sources: https://stripe.com/gb/pricing and https://stripe.com/gb/billing/pricing.

At a small subscription value, the fixed 20p transaction component matters. For planning only, a £7 monthly card subscription paid by an international card with no conversion would pay about £0.42 in the card fee, plus around £0.05 in Stripe Billing usage fee; roughly £6.53 remains before tax, refunds, disputes, data, infrastructure and support. The actual charge depends on the card's country, account price list, conversion and product configuration.

For digital subscriptions sold to EU consumers, investigate VAT registration/collection and the Non-Union One Stop Shop where applicable. EU guidance says the OSS can cover consumer services sold by businesses established outside the EU: https://vat-one-stop-shop.ec.europa.eu/one-stop-shop_en. Sales tax rules can also arise in other markets.

## 4. Economics at 1,000 active subscribers

Gross recurring revenue, before churn, payment fees, refunds, VAT/sales taxes, data and operating costs:

| Monthly price per paying user | Monthly recurring revenue | Annualised recurring revenue |
|---:|---:|---:|
| £7 | £7,000 | £84,000 |
| £8 | £8,000 | £96,000 |
| £10 | £10,000 | £120,000 |
| €7 | €7,000 | €84,000 |
| €10 | €10,000 | €120,000 |

At 1,000 paying subscribers, this is a meaningful business target but not multibillion-naira revenue. A multibillion-naira **valuation** could be mathematically possible at a valuation multiple and exchange rate that support it, but the multiple is not guaranteed; it would depend on recurring revenue quality, churn, growth, margins, concentration, ownership and investor demand. With no paying cohort or retention data yet, a multibillion-naira valuation within 18 months is an ambitious upside case, not a forecast.

### Illustrative valuation versus revenue scenario (not a forecast)

Using a **made-up planning exchange rate of ₦2,000 per £1** solely to show the arithmetic, 1,000 subscribers paying £7–£10 create £84,000–£120,000 ARR, equivalent to ₦168m–₦240m annual gross revenue. At a hypothetical 5× ARR valuation multiple, that produces a £420,000–£600,000 enterprise-value illustration (₦840m–₦1.2bn at that assumed exchange rate). At 10× ARR, the illustration would be ₦1.68bn–₦2.4bn. Actual private-company valuations may be much lower or higher; the multiple and exchange rate are assumptions, not market promises.

At an £8/month average price, roughly **10,417 active paying subscribers** would be needed for £1m ARR (about ₦2bn annual gross revenue at the same illustrative ₦2,000/£ assumption). Revenue and valuation are separate targets. One thousand subscribers is a strong validation milestone; it is not a guarantee of a multibillion-naira valuation.

Before spending on international incorporation or ads, validate the core numbers with a small paid cohort: conversion to paid, monthly churn, reports run per subscriber, API cost per active user, payment success rate and gross margin.

## 5. Persona and acquisition implications

- **Persona A (evidence-seeking researcher):** sells the time-saving research card and transparent evidence trail.
- **Persona C (football publisher):** sells repeatable research, source provenance and a workflow to make responsible, differentiated content. Test a creator tier only if interviews reveal a higher-volume need.
- **Persona B (free-first / tip-seeking user, if research validates this framing):** don't let a free tier become unlimited live data plus expensive reports. Offer a sample report or a narrowly capped trial, with clear limits. Do not assume all Persona B users refuse to pay; interview and measure them.
- Tuesday/Wednesday paid acquisition for A and C is a testable hypothesis, not a rule. Only scale after measuring paid conversion, CAC payback and retention. The product should not need a massive free audience to survive.

## 6. Country launch and betting-marketing caution

This is a preliminary product-planning screen, not legal advice. We are selling a research subscription, not taking deposits or placing bets. However, marketing that looks like paid betting tips or makes claims about picks can still attract advertising scrutiny.

- **UK first for validation:** the £ pricing and EPL-first positioning align. UK ASA/CAP advice says tipster-style promotions should not imply guaranteed success or likely profit, should not exaggerate winnings, and should substantiate historical claims. See https://www.asa.org.uk/advice-online/betting-and-gaming-tipsters.html. Keep reports evidence-led and avoid “sure win”, income or profit claims.
- **US/Canada:** do not assume one uniform national rule for sports betting promotion; launch deliberately by jurisdiction and review ad, affiliate and consumer-subscription rules before targeting particular states/provinces.
- **EU/EEA:** start with a small set of countries only after VAT and consumer-cancellation rules are assessed. EU guidance says the One Stop Shop can support non-EU businesses supplying digital services to consumers across EU member states: https://vat-one-stop-shop.ec.europa.eu/one-stop-shop_en.
- **Australia:** defer as an initial market. ACMA says reforms passed on 19 August 2026 will bring additional gambling-advertising restrictions and affiliate-related reforms, most commencing 1 January 2027. Their application to a research-only subscription depends on the actual product and marketing, so review locally before entry: https://www.acma.gov.au/about-interactive-gambling-act.

The first release should not place bets, hold customer betting funds, link to illegal operators, or promise profit. Require adults only if that fits the final product/legal review, and include responsible-use and uncertainty language.

## 7. Current priority and social media pause

Social media automation, publishing calendars and boosting posts are deferred. Do not allocate build time or ad budget to them until the paid research flow, data licence, billing and retention are validated. Tuesday/Wednesday advertising remains a later experiment, not a current task.

## 8. Android app foundation

The parallel native Android project lives in `../MatchSieve-Mobile/`. It is a Kotlin/Jetpack Compose scaffold only. It contains the market-selection UI and typed client models for a future hosted API; it is not yet wired to real fixtures, subscriptions or the report endpoint. The public API, authentication, billing webhook and subscription entitlement must be server-side. The current local Python prototype should remain local-only until properly secured and deployed.
