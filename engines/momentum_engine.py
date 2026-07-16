from engines.base_engine import BaseEngine


class MomentumEngine(BaseEngine):

    def __init__(self):
        super().__init__("Momentum Engine")

    def calculate(self, context):

        features = context.features

        score = 50
        reasons = []

        # ----------------------------------
        # Weighted Form
        # ----------------------------------

        form = (
            features.home_weighted_form +
            features.away_weighted_form
        ) / 2

        if form >= 80:
            score += 20
            reasons.append("Excellent recent form")

        elif form >= 65:
            score += 10
            reasons.append("Good recent form")

        elif form <= 40:
            score -= 15
            reasons.append("Poor recent form")

        # ----------------------------------
        # Goal Average
        # ----------------------------------

        if features.total_goal_average >= 3:
            score += 10
            reasons.append("Goals trending upward")

        elif features.total_goal_average <= 2:
            score -= 10
            reasons.append("Goals trending downward")

        # ----------------------------------
        # Attack Strength
        # ----------------------------------

        if features.attack_strength >= 75:
            score += 15
            reasons.append("Strong attack")

        elif features.attack_strength <= 40:
            score -= 10
            reasons.append("Weak attack")

        # ----------------------------------
        # Defence Strength
        # ----------------------------------

        if features.defence_strength >= 75:
            score -= 5
            reasons.append("Strong defensive teams")

        # ----------------------------------
        # Goal Probability
        # ----------------------------------

        if features.goal_probability >= 75:
            score += 10
            reasons.append("High goal probability")

        elif features.goal_probability <= 30:
            score -= 10
            reasons.append("Low goal probability")

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        if score >= 85:
            trend = "EXPLODING"

        elif score >= 70:
            trend = "RISING"

        elif score >= 45:
            trend = "STABLE"

        elif score >= 25:
            trend = "DECLINING"

        else:
            trend = "FREE FALL"

        features.momentum = trend

        return {

            "score": score,

            "trend": trend,

            "reasons": reasons

        }