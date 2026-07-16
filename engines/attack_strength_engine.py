from engines.base_engine import BaseEngine


class AttackStrengthEngine(BaseEngine):

    def __init__(self):
        super().__init__("Attack Strength Engine")

    def calculate(self, context):

        features = context.features

        score = 50
        reasons = []

        # ----------------------------------
        # Goal Average
        # ----------------------------------

        avg = (
            features.home_goal_average +
            features.away_goal_average
        ) / 2

        if avg >= 2.2:
            score += 20
            reasons.append("Excellent scoring average")

        elif avg >= 1.6:
            score += 10
            reasons.append("Good scoring average")

        elif avg <= 1.0:
            score -= 15
            reasons.append("Poor scoring average")

        # ----------------------------------
        # xG
        # ----------------------------------

        if features.total_xg >= 3:
            score += 15
            reasons.append("High expected goals")

        elif features.total_xg <= 1.5:
            score -= 10
            reasons.append("Low expected goals")

        # ----------------------------------
        # Shots
        # ----------------------------------

        if features.total_shots >= 24:
            score += 10
            reasons.append("High shot volume")

        elif features.total_shots <= 10:
            score -= 8
            reasons.append("Low shot volume")

        # ----------------------------------
        # Shots on Target
        # ----------------------------------

        if features.total_sot >= 10:
            score += 15
            reasons.append("High shot accuracy")

        elif features.total_sot <= 4:
            score -= 10
            reasons.append("Poor shot accuracy")

        # ----------------------------------
        # Dangerous Attacks
        # ----------------------------------

        if features.total_dangerous_attacks >= 80:
            score += 10
            reasons.append("High attacking pressure")

        elif features.total_dangerous_attacks <= 40:
            score -= 10
            reasons.append("Low attacking pressure")

        # ----------------------------------
        # Momentum
        # ----------------------------------

        if features.momentum == "RISING":
            score += 10
            reasons.append("Positive momentum")

        elif features.momentum == "DECLINING":
            score -= 10
            reasons.append("Negative momentum")

        score = max(0, min(100, score))

        features.attack_strength = score

        return {

            "score": score,

            "rating": (
                "ELITE" if score >= 90 else
                "HIGH" if score >= 75 else
                "MEDIUM" if score >= 55 else
                "LOW"
            ),

            "reasons": reasons

        }