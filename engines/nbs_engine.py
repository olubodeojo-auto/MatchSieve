from engines.base_engine import BaseEngine


class NBSEngine(BaseEngine):

    def __init__(self):
        super().__init__("NBS Engine")

    def calculate(self, context):

        features = context.features

        score = 0
        reasons = []

        if features.home_team:
            score += 10
            reasons.append("Home team available")

        if features.away_team:
            score += 10
            reasons.append("Away team available")

        if features.league:
            score += 10
            reasons.append("League available")

        if features.venue:
            score += 5
            reasons.append("Venue available")

        if features.status:
            score += 10
            reasons.append("Match status available")

        if features.total_xg > 0:
            score += 10
            reasons.append("xG available")

        if features.home_odds > 0:
            score += 10
            reasons.append("Odds available")

        if features.provider_agreement >= 80:
            score += 15
            reasons.append("Provider agreement")

        if features.data_quality >= 80:
            score += 10
            reasons.append("High data quality")

        if features.market_stability == "VOLATILE":
            score -= 15
            reasons.append("Volatile betting market")

        score = max(0, min(score, 100))

        if score >= 85:
            risk = "LOW"

        elif score >= 65:
            risk = "MEDIUM"

        else:
            risk = "HIGH"

        return {

            "score": score,

            "risk": risk,

            "reasons": reasons

        }