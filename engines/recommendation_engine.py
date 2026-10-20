from engines.base_engine import BaseEngine


class RecommendationEngine(BaseEngine):

    def __init__(self):
        super().__init__("Recommendation Engine")

    def calculate(self, context):

        results = context.results
        features = context.features

        score = 0
        reasons = []

        goal = results.get(
            "Goal Probability Engine",
            {}
        ).get("score", 0)

        under = results.get(
            "Under Engine",
            {}
        ).get("score", 0)

        confidence = results.get(
            "Confidence Engine",
            {}
        ).get("score", 0)

        trap = results.get(
            "Trap Engine",
            {}
        ).get("score", 0)

        explosion = results.get(
            "Explosion Engine",
            {}
        ).get("score", 0)

        if goal >= 85:
            score += 30
            reasons.append("Elite goal probability")

        elif goal >= 70:
            score += 20
            reasons.append("High goal probability")

        if confidence >= 85:
            score += 25
            reasons.append("High confidence")

        elif confidence >= 70:
            score += 15
            reasons.append("Good confidence")

        if features.market_stability == "STABLE":
            score += 10
            reasons.append("Stable market")

        if trap >= 70:
            score -= 30
            reasons.append("Trap detected")

        if explosion >= 80:
            score += 10
            reasons.append("Explosion potential")

        score = max(0, min(score, 100))

        availability = getattr(features, "data_availability", {}) or {}
        usable_evidence = any(availability.get(key) for key in (
            "xg", "goal_averages", "btts_rate", "shots", "dangerous_attacks"
        ))

        if not usable_evidence:
            recommendation = "WAIT"
            reasons.append("Insufficient verified match evidence; no selection issued")
        elif trap >= 75:

            recommendation = "AVOID"

        elif score >= 85:

            recommendation = "ENTER"

        elif score >= 70:

            recommendation = "OVER LEAN"

        elif under >= 85:

            recommendation = "UNDER LEAN STRONG"

        elif under >= 70:

            recommendation = "UNDER LEAN"

        else:

            recommendation = "WAIT"

        return {

            "score": score,

            "recommendation": recommendation,

            "reasons": reasons

        }