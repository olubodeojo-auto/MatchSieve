from engines.base_engine import BaseEngine


class ConfidenceEngine(BaseEngine):

    def __init__(self):
        super().__init__("Confidence Engine")

    def calculate(self, context):

        features = context.features

        score = 50
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
            score += 10
            reasons.append("Venue available")

        if features.status:
            score += 10
            reasons.append("Status available")

        if features.total_xg > 0:
            score += 10
            reasons.append("xG available")

        if (
            features.home_odds > 0 and
            features.draw_odds > 0 and
            features.away_odds > 0
        ):
            score += 10
            reasons.append("Odds available")

        if features.home_probability > 0:
            score += 10
            reasons.append("Probability data available")

        if features.data_quality >= 80:
            score += 10
            reasons.append("Good data quality")

        if features.provider_agreement >= 80:
            score += 10
            reasons.append("Provider agreement")

        score = min(score, 100)

        return {
            "score": score,
            "reasons": reasons
        }