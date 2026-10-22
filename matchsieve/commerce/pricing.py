from __future__ import annotations

from copy import deepcopy

# MatchSieve is deliberately launching with one premium UK offer, not cheap credits,
# matchday passes or a multi-country price ladder. Prices are proposed pilot terms,
# not validated willingness-to-pay and not live checkout configuration.
#
# Money is represented in minor currency units: GBP= pence. Provider names are
# candidates only: do not activate checkout until category approval, merchant-country
# eligibility, taxes, refunds, webhook verification and contribution margin are checked.

REGION_POLICIES = {
    "GB": {
        "currency": "GBP",
        "locale": "en-GB",
        "providers": ["selar", "flutterwave"],
        "credit_packs": [],
        "access_plans": [
            {
                "code": "gb-research-desk-monthly",
                "amount_minor": 1900,
                "duration_days": 30,
                "billing_interval": "month",
                "reports_per_period": 20,
                "renewal": "monthly until cancelled",
            }
        ],
        "experiment": "GB-PREMIUM-19-A",
        "status": "proposed_pilot_not_live",
        "payment_note": (
            "Not live. Confirm the provider accepts MatchSieve's exact football-research "
            "product, Nigeria-based seller eligibility for UK customers, settlement currency, "
            "tax/refund obligations, and verified server-side purchase events before checkout."
        ),
        "positioning": "Premium evidence-led research for serious-minded adult football researchers.",
    }
}


def get_region_policy(country_code: str) -> dict:
    code = (country_code or "").strip().upper()
    if code == "UK":
        code = "GB"
    if code not in REGION_POLICIES:
        raise KeyError(
            f"No live-launch pricing policy configured for country {code!r}. "
            "MatchSieve is testing the UK offer first; other markets remain closed."
        )
    return deepcopy(REGION_POLICIES[code])


def list_region_policies() -> dict:
    return deepcopy(REGION_POLICIES)
