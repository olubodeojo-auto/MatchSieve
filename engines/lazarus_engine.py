from engines.base_engine import BaseEngine


class LazarusEngine(BaseEngine):

    def __init__(self):
        super().__init__("Lazarus Engine")

    def calculate(self, context):

        features = context.features

        score = 0
        reasons = []

        # ----------------------------------
        # Expected Goals
        # ----------------------------------

        total_xg = (
            getattr(features, "home_xg", 0) +
            getattr(features, "away_xg", 0)
        )

        if total_xg >= 2.8:
            score += 20
            reasons.append("High expected goals")

        elif total_xg >= 2.2:
            score += 12
            reasons.append("Good expected goals")

        # ----------------------------------
        # Goal Expectancy
        # ----------------------------------

        goal_expectancy = getattr(features, "goal_expectancy", 0)

        if goal_expectancy >= 3:
            score += 15
            reasons.append("High goal expectancy")

        elif goal_expectancy >= 2:
            score += 8
            reasons.append("Moderate goal expectancy")

        # ----------------------------------
        # Attack Strength
        # ----------------------------------

        attack = max(

            getattr(features, "home_attack_strength", 0),
            getattr(features, "away_attack_strength", 0)

        )

        if attack >= 80:
            score += 20
            reasons.append("Elite attack present")

        elif attack >= 60:
            score += 10
            reasons.append("Strong attack")

        # ----------------------------------
        # Momentum
        # ----------------------------------

        momentum = max(

            getattr(features, "home_momentum", 0),
            getattr(features, "away_momentum", 0)

        )

        if momentum >= 70:
            score += 15
            reasons.append("High attacking momentum")

        elif momentum >= 55:
            score += 8
            reasons.append("Positive momentum")

        # ----------------------------------
        # Match Situation
        # ----------------------------------

        total_score = (
            getattr(features, "home_score", 0) +
            getattr(features, "away_score", 0)
        )

        if total_score <= 1:
            score += 10
            reasons.append("Game still alive for late goal")

        # ----------------------------------
        # Market
        # ----------------------------------

        favourite = getattr(features, "favorite", "")

        if favourite in ("HOME", "AWAY"):
            score += 5
            reasons.append("Market expects a stronger side")

        # ----------------------------------
        # Confidence
        # ----------------------------------

        confidence = getattr(features, "confidence", 0)

        if confidence >= 80:
            score += 10
            reasons.append("Reliable supporting data")

        # ----------------------------------
        # Clamp
        # ----------------------------------

        score = max(0, min(score, 100))

        if score >= 85:
            rating = "VERY HIGH"

        elif score >= 70:
            rating = "HIGH"

        elif score >= 55:
            rating = "MEDIUM"

        else:
            rating = "LOW"

        return {

            "score": score,

            "rating": rating,

            "late_goal": score >= 70,

            "reasons": reasons

        }