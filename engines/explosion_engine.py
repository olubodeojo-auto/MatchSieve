from engines.base_engine import BaseEngine


class ExplosionEngine(BaseEngine):

    def __init__(self):
        super().__init__("Explosion Engine")

    def calculate(self, context):

        features = context.features

        score = 0
        reasons = []

        # ----------------------------------
        # Goal Probability
        # ----------------------------------

        if features.goal_probability >= 80:
            score += 25
            reasons.append("Very high goal probability")

        elif features.goal_probability >= 65:
            score += 15
            reasons.append("High goal probability")

        # ----------------------------------
        # Attack Strength
        # ----------------------------------

        if features.attack_strength >= 80:
            score += 20
            reasons.append("Strong attacking teams")

        elif features.attack_strength >= 65:
            score += 10
            reasons.append("Good attacking teams")

        # ----------------------------------
        # Defence Strength
        # ----------------------------------

        if features.defence_strength <= 40:
            score += 20
            reasons.append("Weak defensive teams")

        elif features.defence_strength <= 60:
            score += 10
            reasons.append("Average defensive teams")

        # ----------------------------------
        # BTTS
        # ----------------------------------

        if features.btts_rate >= 70:
            score += 10
            reasons.append("High BTTS trend")

        # ----------------------------------
        # Momentum
        # ----------------------------------

        if features.momentum == "EXPLODING":
            score += 20
            reasons.append("Momentum exploding")

        elif features.momentum == "RISING":
            score += 10
            reasons.append("Momentum rising")

        # ----------------------------------
        # League Profile
        # ----------------------------------

        league = context.results.get("League Profile Engine", {})

        if league.get("rating") == "HIGH":
            score += 10
            reasons.append("High-scoring league")

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        if score >= 90:
            risk = "EXTREME"

        elif score >= 75:
            risk = "VERY HIGH"

        elif score >= 60:
            risk = "HIGH"

        elif score >= 40:
            risk = "MEDIUM"

        else:
            risk = "LOW"

        features.explosion_risk = score

        return {

            "score": score,

            "risk": risk,

            "reasons": reasons

        }