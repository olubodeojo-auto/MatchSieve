from engines.base_engine import BaseEngine


class RecommendationEngine(BaseEngine):

    def __init__(self):
        super().__init__("Recommendation Engine")

    def calculate(self, features):

        score = 0
        reasons = []

        if features.goal_probability >= 85:
            score += 30
            reasons.append("High goal probability")

        if features.confidence >= 85:
            score += 25
            reasons.append("High confidence")

        if features.market_stability == "STABLE":
            score += 25
            reasons.append("Stable market")

        if features.attack_strength > 1:
            score += 10
            reasons.append("Strong attack profile")

        if features.total_goal_average >= 2.7:
            score += 10
            reasons.append("High goal average")

        if score >= 90:
            recommendation = "ENTER"

        elif score >= 75:
            recommendation = "OVER LEAN"

        elif features.under25 >= 85:
            recommendation = "UNDER LEAN STRONG"

        elif features.under25 >= 70:
            recommendation = "UNDER LEAN"

        elif features.market_stability == "VOLATILE":
            recommendation = "WAIT"

        else:
            recommendation = "AVOID"

        return {
            "score": score,
            "recommendation": recommendation,
            "reasons": reasons
        }