# Specialist agents and regional commerce — local integration handoff

## Separate responsibilities

1. Data collection: source-specific fetch/capture only; raw payload and provenance retained. Optional Soccerway Playwright capture records visible text from the match page and likely same-host detail tabs. It does not claim raw text is structured or verified.
2. Data quality: required-field checks, freshness warnings and conflicts. It can mark records unusable; it cannot choose a market.
3. QQR research: uses only records marked usable, separates supporting and counter-evidence, records gaps, supports 1X2, Double Chance, Draw No Bet, match-goals Over/Under and team-goals Over/Under. It does not display probabilities or manufacture a lean.
4. Report writing: presents the structured research brief and source attribution. It cannot change the recommendation status or add facts.
5. Pipeline: orchestrates all four stages and marks reports for human review. Existing legacy report generation remains separate; this code does not silently replace it.

## Run the specialist pipeline locally

From the repository root, with the branch checked out:

    python scripts/run_agent_pipeline.py path/to/your-collection.json --market OVER_UNDER_MATCH_GOALS

Use a collection JSON exported from real source records. Do not label mock data as real match evidence. The runner writes a JSON audit artifact and a Markdown report. Add --advice-requested only when the user explicitly asks for a view; the current QQR stage still refuses to invent a lean when explicit market-specific evidence is missing.

For Soccerway capture, install Playwright and its Chromium browser in the local environment, then call DataCollectionAgent.collect_soccerway_page(url). This method captures text only; a parser and quality review must precede research. It intentionally does not bypass logins, CAPTCHAs or access controls.

## Regional credit packs and matchday pass

The country policy is in matchsieve/commerce/pricing.py. The current amounts are test hypotheses only. Packs grant 2 or 6 report credits; the matchday pass grants 5 credits for 24 hours, not unlimited access. Unknown country codes fail closed.

CommerceStore stores funnel events and an idempotent credit ledger. The payment-grant method must only be called after a signed payment-provider webhook is verified server-side. It does not validate signatures itself. It is not yet a secure public billing system.

## Events to record

- report_view
- cta_click
- checkout_start
- purchase_completed
- report_repeat_purchase
- purchase_failed
- credit_spent

Segment each event by validated country, currency, experiment, product and persona/campaign where available. Never put card data, passwords, access tokens or full IP addresses into analytics. Use server-side payment confirmation as the source of truth for completed purchases.

## Not yet a production paywall

The existing web server is a local-development service and has no customer authentication, tenant isolation or payment webhook verification. This change intentionally does not pretend a client-side button or redirect is a paid transaction. Before a public paid launch, integrate a payment provider that explicitly accepts the exact product, verify webhook signatures, connect authenticated user IDs to entitlements, and gate report generation and report history server-side. Until then, pricing policy and credit accounting are groundwork only; do not expose the local server publicly.

## Pricing research limits

See REGIONAL_PRICING_AND_COMPETITOR_RESEARCH.md. Public competitor prices are observations, not proof of market share. Competitor subscriber counts and revenue were not reliably disclosed in the pricing pages reviewed, so no user counts are fabricated. Revenue scenarios are arithmetic, not forecasts.
