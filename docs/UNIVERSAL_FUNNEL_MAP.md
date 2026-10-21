# MatchSieve Universal Funnel Map

**Version:** 1.0  
**Date:** 21 October 2026  
**Status:** Funnel specification and design direction. Prices are hypotheses. No payment, opt-in, CRM or community automation is live from this document.

## Executive decision

Build **one account, one core product, one evidence standard, and three persona-specific acquisition paths**. Do not create three separate products or launch a high-ticket coaching funnel and SaaS funnel simultaneously.

The product truth remains:

> MatchSieve organises available football evidence around the fixture and market question a user chooses, then shows supporting signals, counter-evidence, source context and missing inputs in one readable research brief.

The conversion mechanism is to let users inspect the work before asking them to pay. Sell repeatable research value, not guaranteed predictions, a lucky outcome, or “safe” betting.

### Launch-market decision

**Primary commercial test: United Kingdom first**, initially English Premier League research. Use organic search, interviews, relevant creator outreach and a small adult-only pilot first. Do not begin broad paid ads until the exact offer and copy have been reviewed for UK betting-adjacent rules and the product's payment processor has confirmed acceptance.

Keep Nigeria, Ghana and Kenya as separately measured audience tests / later market cohorts, rather than applying one price to the entire continent. The founder's location does not have to dictate the first customer's location. The decision is driven by the proposed GBP subscription model, but the UK has stricter marketing scrutiny in this category; if compliance clearance fails, pause paid promotion and reassess a non-forecasting product position or another market with local review.

### The core principle

A user may arrive from any channel. The funnel preserves attribution and adapts the message to the user's job, but does not create separate databases, payment rules or research engines.

## Universal customer journey

1. **Arrival:** save consented UTM campaign/source, landing variant, selected persona path and explicitly selected or validated market. Do not depend on hidden IP geolocation alone.
2. **Orient:** explain MatchSieve in one sentence. One primary CTA. Avoid feature walls and fake social proof.
3. **Proof:** show a real, manually reviewed and appropriately licensed sample report. Display its fixture/date, data window, source notes, sample size and missing-data limitations. A synthetic prototype can only be labelled as a UI demonstration, never as a real match or customer result.
4. **Opt in:** offer Stop Guessing the Odds — The Football Betting Maths Playbook and a reviewed sample report. Collect only the email and the minimum useful preference (researcher / comparator / publisher). Keep marketing email consent separate from delivery of the requested resource.
5. **Lead thank-you:** explain what happens next, provide the resource only when the delivery mechanism exists, offer an optional free community link, and show the next useful step.
6. **Nurture:** a short, consented sequence teaches the report method, shows an actual example, answers the free-alternative objection, and invites a first research session. No false scarcity, manufactured countdown, fake user count or pressure to bet.
7. **First useful result:** select fixture → select market → generate and inspect report. Clearly state the report's evidence status and gaps.
8. **Premium offer:** one UK-first Research Desk membership at a proposed £19/month after a real sample and a clear explanation of limits. No economy tripwire, credit pack or matchday pass at launch. Qualify for serious research intent rather than trying to convert every visitor.
9. **Core subscription:** offer the monthly plan after users understand the report's value and expected usage. State renewal, allowance, supported competitions, freshness limitations, taxes where relevant, cancellation and refund policy before purchase.
10. **Payment confirmation:** server-side verified webhook updates payment and entitlement state. A browser redirect alone does not grant access.
11. **Paid thank-you/onboarding:** only after the server confirms a paid/active entitlement, show the correct account access, how to research the first match, and optional paid-community instructions.
12. **Retention:** saved report snapshots, new market-week workflow, user-requested update preferences, transparent source freshness and easy cancellation.
13. **Publisher upsell/referral:** after repeated use demonstrates value, offer a publisher workflow and ask satisfied users to share a sample. Do not sell future/unbuilt export capabilities as available features.

## Traffic paths by persona

All paths share the same account, sample-report standard, billing/entitlement service and report engine.

### Path A — Serious Independent Market Researcher

**Likely incoming intent:** match analysis, football stats, Premier League preview, over/under or BTTS research.

**Headline to test:** “Stop guessing the odds. Examine the evidence.”

**Supporting copy:** “MatchSieve is for serious-minded adults who value evidence more than noise. Inspect the case for a market, the case against it, its source context and what remains unverified.”

**Lead offer:** checklist + reviewed sample report.

**First conversion:** complete one market-specific brief.

**Paid trigger to measure:** the user repeats the job across multiple fixtures or a later match week and can identify the steps MatchSieve replaced.

### Path B — Disciplined Market Comparator

**Incoming intent:** comparing claims, market context, source reliability or competing interpretations.

**Headline to test:** “More opinions are not the same as more evidence.”

**Supporting copy:** “Inspect what supports a football-market argument, what pushes back and what remains unknown. MatchSieve makes the reasoning easier to inspect; it doesn't ask you to accept a pick on faith.”

**Lead offer:** checklist / report-reading guide demonstrating sample sizes and counter-evidence.

**Paid trigger to measure:** the user inspects sources and counter-signals, returns to compare another market, and sees a recurring reason to use the archive.

**Guardrail:** do not target people trying to chase losses or imply research can solve financial problems.

### Path C — Football Publisher

**Incoming intent:** football preview, content research, podcaster preparation, community discussion, weekly fixture roundup.

**Headline to test:** “Research the match. Keep the sources. Make the argument yours.”

**Supporting copy:** “Start with a structured fixture-and-market research brief. Review evidence on both sides and retain source notes before writing your own preview or discussion.”

**Lead offer:** publisher research checklist and report-format sample.

**Paid trigger to measure:** repeated use across real publishing deadlines, source checking and the ability to reuse a consistent report structure.

**Later paid upgrade:** higher allowance and a batch research workflow. Export and republishing claims must be limited by actual data-provider licences; a subscription does not automatically transfer data rights.

## Premium UK launch offer — one hypothesis

The funnel preview is a design concept. The £19 price is a commercial hypothesis, not validated willingness-to-pay and not a live offer.

| Level | Working offer | Test price | Intended job | Launch condition |
|---|---|---:|---|---|
| Free | Stop Guessing the Odds — The Football Betting Maths Playbook + reviewed sample | £0 | Demonstrate the method and qualify interest | Resource delivery, privacy and consent flows work |
| Core | MatchSieve Research Desk; proposed cap of 20 full briefs per billing month | £19/month (UK pilot only) | Serve serious independent researchers with a repeat job | Reviewed reports, named competitions, source-rights review, approved payments, secure entitlements and viable service costs |
| Future publisher service | Higher-volume research workflow and source archive/export only where licensed | Not priced or open | Serve repeat publishers with proven workflow needs | Interviews, existing features, permissions, paid-pilot evidence and delivery capacity |

Launch with one premium UK paid choice only. No economy pack, matchday pass or multi-country pricing. Do not show a Publisher tier as purchasable until its workflow, permissions and service costs are validated.

**Do not show “unlimited”.** State the report allowance and supported competitions clearly. Do not sell the proposed £19 offer until its allowance is actually enforced and provider costs, source rights, payment eligibility and cancellation work.

## Geographic routing and pricing

### Decision

Use **campaign and user-selected market routing first**, not hidden IP-based price surprises. An optional country/market picker can localise wording, currency and checkout only after that route has been approved and tested. Preserve the user's chosen path so they are not switched back and forth.

- **Initial live product test:** UK English, GBP plan and UK-specific terms after compliance review.
- **US / Canada / Europe / Australia:** interest or waitlist path until payment processing, tax and advertising checks are complete for that market.
- **Nigeria / Ghana / Kenya:** separate campaign and willingness-to-pay cohort; use local currency only when local gateway settlement and actual costs are confirmed. Do not assume all African customers are price-insensitive or all expect free access.
- **Currency rules:** show the amount the customer will actually be charged, whether taxes are included, renewal currency, and how conversion is handled. Do not use IP alone as the basis for a materially different price without an explicit pricing policy.
- **Attribution:** preserve utm_source, utm_medium, utm_campaign, utm_content, landing variant, persona path, chosen country/market and landing date if consented and permitted. Never place email, payment details or other personal data in UTM parameters.

## Thank-you and payment-state design

### Lead / opt-in thank-you
- Confirm the request only after the backend accepted the opt-in.
- Give the promised resource immediately or say exactly when/how it will arrive.
- Invite, but do not force, a free WhatsApp or Telegram community.
- Keep newsletter/marketing consent separate from resource delivery.
- Offer one next action: inspect the sample or start the first research flow.

### Purchase confirmation
- Grant paid access only when a verified provider webhook or server-to-server confirmation says the transaction is paid and the relevant subscription/entitlement is active.
- Show order/subscription details, plan, renewal amount/cadence, next billing date when available, support contact, and cancellation route.
- Only then show paid-community instructions. Use an expiring/single-use Telegram invite where feasible and re-check entitlement when membership is renewed or cancelled.
- For WhatsApp, community/group links can be forwarded. Treat the app's authenticated entitlement as the source of truth; the community is an optional add-on, not the paywall.

### Pending payment
- Say “Payment is still being confirmed.”
- Do not grant premium access or send premium invite.
- Offer “Check status” with server-side status, and ask the user not to pay again until the status is known.
- If still pending after a threshold, show support instructions.

### Failed/cancelled payment
- Say what failed without blaming the user.
- Provide retry and the free sample/community path.
- Do not send purchase-confirmed emails or grant subscription access.
- Log the provider's event ID idempotently; do not retry-charges automatically.

### Refund, chargeback or subscription cancellation
- Apply the documented policy and current entitlement status.
- Revoke future paid access when provider policy and billing state require it; honour paid-through periods where applicable.
- Do not obstruct cancellation, hide the action or use guilt/countdown copy.
- Keep an audit trail of status transitions, not sensitive card data.

## Funnel email sequence

Only send promotional email when consent and the applicable legal basis are recorded.

1. **Requested resource:** deliver the checklist and a plain explanation of what the sample does/does not prove.
2. **How to inspect a report:** show the market question, source record, data window, supporting and counter-evidence.
3. **The free alternative objection:** acknowledge raw stats are free; explain the paid difference without disparaging free tools.
4. **Try a real report:** direct the reader to select a fixture/market or read a reviewed sample.
5. **Plan invitation:** explain the allowance, price, renewal and cancellation.
6. **Publisher variant:** only for opted-in people who selected that use case; discuss source traceability and repetitive workflow.
7. **Quiet-user message:** optional, useful and respectful; no shame or gambling urgency.
8. **Post-purchase onboarding:** after verified payment only, help the user finish the first report and understand source limitations.
9. **Renewal / cancellation:** transparent notice as legally required; cancellation must be easy and clear.

## Automation and delivery architecture

Use the product backend as the authority for lead, payment and access states; use automation software for notifications and low-risk orchestration, not as the database of record.

**Recommended MVP stack**
- **Landing / funnel:** MatchSieve web frontend. The funnel preview at web/funnel-preview.html is design-only; its forms and payment buttons do not submit data or charge money.
- **Lead capture:** a consent-aware form endpoint and durable database table, with input validation, rate limiting, deduplication, source attribution and privacy/retention rules.
- **Email:** choose one sender/list tool after consent and delivery needs are known. Do not copy all buyers into marketing without consent.
- **Checkout:** no provider has been approved for MatchSieve yet. Ask providers in writing whether they will support the exact market-research/football-analysis product before creating live products or taking payments.
- **Payment events:** signed webhooks, verified signatures, idempotency, subscription status mapping, audit trail and entitlement API.
- **Community:** optional free community after opt-in; paid invite only after confirmed paid state. Telegram Bot API supports expiring/member-limited or join-request invite links when the bot has the correct admin rights. WhatsApp automation should use approved WhatsApp Business Platform methods, user opt-in and current message pricing/policies.
- **Orchestration:** begin with a small number of Zapier workflows if their tasks fit the free allowance; consider n8n Cloud or a securely hosted n8n instance once workflow volume justifies it. The customer app must not depend on the founder's laptop.
- **Analytics:** minimal, consent-aware, event-based funnel measurement. Never log card data, secrets or report free text. Record events such as sample_opened, optin_accepted, research_completed, source_opened, checkout_started, payment_confirmed, subscription_cancelled and refund_confirmed.

### Zapier Free limit

The current Zapier Free plan lists 100 tasks/month, two-step Zaps and a 15-minute polling interval for polling triggers. That is enough to prototype a very light workflow; it is not a safe assumption for a 200–1,000-lead/customer automation system. At 200 leads, even a few tasks each can exceed 100 tasks. Estimate expected tasks from each actual workflow before relying on the plan.

### n8n laptop vs server

- If n8n is self-hosted on the local Windows laptop, that laptop, n8n process and internet connection must remain available for scheduled workflows and webhooks to run. If it sleeps, shuts down or loses connectivity, workflows may not run.
- For production, run n8n Cloud or host self-managed n8n on a reliable cloud VM/VPS with HTTPS, secure credential storage, backups, updates, monitoring, restart policy and access control. A VPS is not “set and forget”.
- Current n8n's pricing page lists a hosted Starter plan with 2,500 monthly workflow executions at €20/month billed annually; confirm live pricing and the expected monthly execution count before choosing it. n8n executions and Zapier tasks are different billing units.

## Ebook decision

Do **not** title an ebook “How to Bet Safely and Compound Daily”. “Safely” can imply betting is safe, and “compound daily” suggests sustained gains that a reader should not expect from uncertain gambling outcomes. It would also attract a more profit-seeking and potentially vulnerable audience than our evidence-first product should target.

Better lead asset: **The 7-Point Match Research Checklist**. It is directly aligned with the product.

A separate educational ebook can be tested later with a title like **Football Markets, Variance and Bankroll Maths: How to Read Evidence Without Mistaking a Pattern for a Promise**. It should explain odds, variance, sample-size traps, uncertainty, responsible limits and how losses can occur; no fixed daily growth, guaranteed profit, or loss-recovery strategy. Confirm platform rules for the book's exact content before selling it.

## B2B coaching, $1k–$2k sales and white-label

These are **not the first MatchSieve funnel**. They are potential separate business offers.

### Coaching / consulting funnel (later)
A legitimate high-ticket offer needs a business outcome the seller can deliver and evidence for that promise. A possible concept is a **Football Publisher Research Workflow Sprint** for established publishers: audit their research process, define source and editorial checks, set up a repeatable research pipeline, and train their team. Do not sell “earn $2,000 from betting” coaching or promise revenue outcomes.

Use this path only after proof exists:
targeted B2B outreach → case study / diagnostic → application form → discovery call → scoped proposal → terms and payment → onboarding → delivery → review/referral.

A $1,000–$2,000 price requires the scope, delivery hours, rights, support window and measurable business value to justify it. First run a few founder-led paid pilots. Do not hire an expensive international firm or commission-only closer before the offer converts. If using Upwork for a sales/appointment-setting specialist, write a specific deliverable-based contract, assess previous results, observe the first campaign and follow Upwork's platform payment rules. Do not make commission-only hiring the core growth assumption.

### AI sales agent
Useful early uses: answer approved product FAQs, explain the report workflow, collect a consented lead, route by use case, schedule a call, and hand a human the captured context. It should not invent claims, make guarantees, give personalized betting recommendations or make unsolicited automated calls. For $1k–$2k B2B services, let a human close the first deals until the offer and objection handling are proven.

### White-label
A white-label research/report API or publisher dashboard could later be a B2B offer, but only after source rights, API availability, security, tenant isolation, support, uptime and data permissions are explicit. Do not promise that buyers can remove attribution or redistribute third-party data if their licences forbid it.

Separately, funnel-building services could be sold as a digital agency offer, but that should have a separate landing page and operations from MatchSieve so prospective football research customers are not confused.

## Payment platform / ebook history finding

The Library contains the PDF “After Wisdom Have Sense — Nigeria Edition”, which mentions Payhip product links (including payhip.com/b/lFY45 and payhip.com/b/UhSwY). This proves Payhip was present in the user's material, but does **not** prove those links were the user's own seller account or that it was the exact checkout for that PDF.

The plugin search in ChatGPT did not surface a native Payhip, Gumroad or Amazon publishing/seller-management connector. Payhip does document Zapier integrations and webhooks/API; Gumroad documents Zapier integrations. Those can be used when an account is connected and product policy allows the sale.

**Important platform-policy gate:** Payhip lists gambling and sports forecasting among restricted products. Gumroad specifically lists sports forecasting, picks, predictions, tips, signals and other things that drive a wager as prohibited; its policy does allow some educational writing about bankroll maths and record-keeping. Stripe also lists sports forecasting/odds-making in its prohibited/restricted-business documentation. Do not use Payhip, Gumroad or Stripe for MatchSieve's paid research app without the platform/processor's written assessment of the exact product and sales copy. An educational, non-forecasting research checklist or book may be treated differently, but its final content still needs review.

Official policy links:
- Payhip restricted products: https://help.payhip.com/article/205-what-products-are-not-allowed-on-payhip
- Gumroad prohibited products: https://gumroad.com/prohibited
- Stripe restricted businesses: https://stripe.com/gb/legal/restricted-businesses

## Launch gates before any public paid campaign

1. Verify legal/data-provider rights for the exact competitions, sources and displayed evidence.
2. Obtain written payment-provider approval for the exact described service before accepting money.
3. Confirm the UK marketing/compliance review for the actual copy; the ASA ruled in October 2026 against a football analytics advert that implied users would be very likely to profit from gambling decisions.
4. Implement authenticated access, report ownership, rate limits, billing entitlements, signed/idempotent webhooks and a proper cancellation/refund process.
5. Connect form capture, email delivery and privacy/consent.
6. Test every route: lead submission, duplicate lead, email delivery failure, checkout success, pending, decline, webhook retry/duplicate, refund, cancellation, and attempted access without entitlement.
7. Prove first-report activation and at least early repeat usage with adult customers before scaling ad spend.
8. Measure contribution margin including data API costs, processor fees, tax, hosting, support, refunds and acquisition.

## Success measures

Primary: **paying customers who complete a useful research session, return and renew while contribution margin is positive**.

Supporting measures:
- eligible visitors → sample opened;
- sample opened → opt-in accepted;
- opt-in → first report completed;
- first report → second report in a later week;
- qualified visitor → completed checkout;
- first payment → renewal;
- report cost and data coverage;
- cancellation, refund, complaint and payment failure rates;
- publisher repeat use and referred paying users.

Do not report impressions, Telegram joins, free leads or survey interest as revenue or product-market fit.
