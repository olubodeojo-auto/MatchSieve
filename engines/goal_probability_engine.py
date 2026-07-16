from engines.base_engine import BaseEngine


class GoalProbabilityEngine(BaseEngine):

    def __init__(self):
        super().__init__("Goal Probability Engine")

    def calculate(self, features):

        score = 0
        reasons = []

        # --------------------------
        # Goal Average
        # --------------------------

        if features.total_goal_average >= 3.0:
            score += 25
            reasons.append("Excellent goal average")

        elif features.total_goal_average >= 2.5:
            score += 18
            reasons.append("Good goal average")

        elif features.total_goal_average <= 2.0:
            score -= 15
            reasons.append("Low goal average")

        # --------------------------
        # BTTS
        # --------------------------

        if features.btts_rate >= 70:
            score += 15
            reasons.append("Strong BTTS trend")

        elif features.btts_rate <= 40:
            score -= 10
            reasons.append("Poor BTTS trend")

        # --------------------------
        # Attack Strength
        # --------------------------

        if features.attack_strength >= 80:
            score += 15
            reasons.append("Strong attack")

        elif features.attack_strength <= 40:
            score -= 10
            reasons.append("Weak attack")

        # --------------------------
        # Defence
        # --------------------------

        if features.defence_strength <= 40:
            score += 10
            reasons.append("Weak defence")

        elif features.defence_strength >= 80:
            score -= 8
            reasons.append("Strong defence")

        # --------------------------
        # xG
        # --------------------------

        if features.total_xg >= 3:
            score += 15
            reasons.append("High xG")

        elif features.total_xg <= 1.8:
            score -= 10
            reasons.append("Low xG")

        # --------------------------
        # Shots on Target
        # --------------------------

        if features.total_sot >= 10:
            score += 10
            reasons.append("High shots on target")

        elif features.total_sot <= 5:
            score -= 8
            reasons.append("Low shots on target")

        # --------------------------
        # Dangerous Attacks
        # --------------------------

        if features.total_dangerous_attacks >= 80:
            score += 10
            reasons.append("High attacking pressure")

        elif features.total_dangerous_attacks <= 40:
            score -= 8
            reasons.append("Low attacking pressure")

        # --------------------------
        # Momentum
        # --------------------------

        if features.momentum == "RISING":
            score += 8
            reasons.append("Positive momentum")

        elif features.momentum == "DECLINING":
            score -= 8
            reasons.append("Negative momentum")

        # --------------------------
        # Clamp Score
        # --------------------------

        score = max(0, min(100, score))

        return {

            "score": score,

            "probability": score,

            "reasons": reasons

        }