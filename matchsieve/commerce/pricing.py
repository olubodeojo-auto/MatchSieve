from __future__ import annotations
from copy import deepcopy

# Hypotheses only. amount_minor uses currency minor units (UGX has no fractional unit).
REGION_POLICIES = {
 "NG":{"currency":"NGN","locale":"en-NG","single_credit_pack":{"amount_minor":30000,"credits":2},"larger_credit_pack":{"amount_minor":70000,"credits":6},"matchday_pass":{"amount_minor":50000,"credits":5,"valid_hours":24},"experiment":"NG-A","status":"pilot_hypothesis"},
 "GH":{"currency":"GHS","locale":"en-GH","single_credit_pack":{"amount_minor":200,"credits":2},"larger_credit_pack":{"amount_minor":500,"credits":6},"matchday_pass":{"amount_minor":400,"credits":5,"valid_hours":24},"experiment":"GH-A","status":"pilot_hypothesis"},
 "KE":{"currency":"KES","locale":"en-KE","single_credit_pack":{"amount_minor":2000,"credits":2},"larger_credit_pack":{"amount_minor":5000,"credits":6},"matchday_pass":{"amount_minor":4000,"credits":5,"valid_hours":24},"experiment":"KE-A","status":"pilot_hypothesis"},
 "UG":{"currency":"UGX","locale":"en-UG","single_credit_pack":{"amount_minor":10,"credits":2},"larger_credit_pack":{"amount_minor":25,"credits":6},"matchday_pass":{"amount_minor":20,"credits":5,"valid_hours":24},"experiment":"UG-A","status":"pilot_hypothesis"},
 "GB":{"currency":"GBP","locale":"en-GB","single_credit_pack":{"amount_minor":79,"credits":2},"larger_credit_pack":{"amount_minor":199,"credits":6},"matchday_pass":{"amount_minor":149,"credits":5,"valid_hours":24},"experiment":"GB-A","status":"pilot_hypothesis"},
 "US":{"currency":"USD","locale":"en-US","single_credit_pack":{"amount_minor":99,"credits":2},"larger_credit_pack":{"amount_minor":249,"credits":6},"matchday_pass":{"amount_minor":199,"credits":5,"valid_hours":24},"experiment":"US-A","status":"pilot_hypothesis"},
 "CA":{"currency":"CAD","locale":"en-CA","single_credit_pack":{"amount_minor":129,"credits":2},"larger_credit_pack":{"amount_minor":299,"credits":6},"matchday_pass":{"amount_minor":249,"credits":5,"valid_hours":24},"experiment":"CA-A","status":"pilot_hypothesis"},
 "AE":{"currency":"AED","locale":"en-AE","single_credit_pack":{"amount_minor":300,"credits":2},"larger_credit_pack":{"amount_minor":700,"credits":6},"matchday_pass":{"amount_minor":500,"credits":5,"valid_hours":24},"experiment":"AE-A","status":"pilot_hypothesis"},
 "DE":{"currency":"EUR","locale":"de-DE","single_credit_pack":{"amount_minor":79,"credits":2},"larger_credit_pack":{"amount_minor":199,"credits":6},"matchday_pass":{"amount_minor":149,"credits":5,"valid_hours":24},"experiment":"EU-A","status":"pilot_hypothesis"},
 "FR":{"currency":"EUR","locale":"fr-FR","single_credit_pack":{"amount_minor":79,"credits":2},"larger_credit_pack":{"amount_minor":199,"credits":6},"matchday_pass":{"amount_minor":149,"credits":5,"valid_hours":24},"experiment":"EU-A","status":"pilot_hypothesis"},
 "ES":{"currency":"EUR","locale":"es-ES","single_credit_pack":{"amount_minor":79,"credits":2},"larger_credit_pack":{"amount_minor":199,"credits":6},"matchday_pass":{"amount_minor":149,"credits":5,"valid_hours":24},"experiment":"EU-A","status":"pilot_hypothesis"},
}
def get_region_policy(country_code: str) -> dict:
    code = (country_code or "").strip().upper()
    if code not in REGION_POLICIES:
        raise KeyError(f"No pricing policy configured for country {code!r}.")
    return deepcopy(REGION_POLICIES[code])
def list_region_policies() -> dict:
    return deepcopy(REGION_POLICIES)
