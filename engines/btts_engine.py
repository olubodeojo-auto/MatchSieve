from engines.base_engine import BaseEngine


class BTTSEngine(BaseEngine):

    def __init__(self):
        super().__init__("BTTS Engine")

    def calculate(self, context):

        features = context.features

        score = 50
        reasons = []

        # -----------------------
        # BTTS History
        # -----------------------

        if features.btts_rate >= 75:
            score += 20
            reasons.append("Excellent BTTS history")

        elif features.btts_rate >= 60:
            score += 10
            reasons.append("Good BTTS history")

        elif features.btts_rate <= 40:
            score -= 15
            reasons.append("Poor BTTS history")

        # -----------------------
        # Goal Average
        # -----------------------

        if features.total_goal_average >= 3.0:
            score += 15
            reasons.append("High goal average")

        elif features.total_goal_average <= 2.0:
            score -= 10
            reasons.append("Low goal average")

        # -----------------------
        # Attack Strength
        # -----------------------

        if features.attack_strength >= 80:
            score += 15
            reasons.append("Strong attacking teams")

        elif features.attack_strength <= 40:
            score -= 10
            reasons.append("Weak attacking teams")

        # -----------------------
        # Defence Strength
        # -----------------------

        if features.defence_strength <= 40:
            score += 10
            reasons.append("Weak defensive teams")

        elif features.defence_strength >= 80:
            score -= 10
            reasons.append("Strong defensive teams")

        # -----------------------
        # xG
        # -----------------------

        if features.total_xg >= 2.8:
            score += 10
            reasons.append("High xG")

        elif features.total_xg <= 1.8:
            score -= 8
            reasons.append("Low xG")

        # -----------------------
        # Momentum
        # -----------------------

        if features.momentum == "RISING":
            score += 8
            reasons.append("Positive momentum")

        elif features.momentum == "DECLINING":
            score -= 8
            reasons.append("Negative momentum")

        # -----------------------
        # Clamp
        # -----------------------

        score = max(0, min(score, 100))

        stars = round(score / 20)

        return {

            "score": score,

            "stars": stars,

            "yes": score >= 65,

            "no": score < 50,

            "reasons": reasons

        }