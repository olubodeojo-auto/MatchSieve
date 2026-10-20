from engines.base_engine import BaseEngine


class GoalProbabilityEngine(BaseEngine):

    def __init__(self):
        super().__init__("Goal Probability Engine")

    def calculate(self, context):
        features = context.features
        available = getattr(features, "data_availability", {}) or {}
        score = 0
        reasons = []
        evidence_available = False

        if available.get("goal_averages"):
            evidence_available = True
            if features.total_goal_average >= 3.0:
                score += 25
                reasons.append("Excellent goal average")
            elif features.total_goal_average >= 2.5:
                score += 18
                reasons.append("Good goal average")
            elif features.total_goal_average <= 2.0:
                score -= 15
                reasons.append("Low goal average")

        if available.get("btts_rate"):
            evidence_available = True
            if features.btts_rate >= 70:
                score += 15
                reasons.append("Strong BTTS trend")
            elif features.btts_rate <= 40:
                score -= 10
                reasons.append("Poor BTTS trend")

        if available.get("xg"):
            evidence_available = True
            if features.attack_strength >= 80:
                score += 15
                reasons.append("Strong attack")
            elif features.attack_strength <= 40:
                score -= 10
                reasons.append("Weak attack")

            if features.defence_strength <= 40:
                score += 10
                reasons.append("Weak defence")
            elif features.defence_strength >= 80:
                score -= 8
                reasons.append("Strong defence")

            if features.total_xg >= 3:
                score += 15
                reasons.append("High xG")
            elif features.total_xg <= 1.8:
                score -= 10
                reasons.append("Low xG")

        if available.get("shots"):
            evidence_available = True
            if features.total_sot >= 10:
                score += 10
                reasons.append("High shots on target")
            elif features.total_sot <= 5:
                score -= 8
                reasons.append("Low shots on target")

        if available.get("dangerous_attacks"):
            evidence_available = True
            if features.total_dangerous_attacks >= 80:
                score += 10
                reasons.append("High attacking pressure")
            elif features.total_dangerous_attacks <= 40:
                score -= 8
                reasons.append("Low attacking pressure")

        if available.get("form") or available.get("xg"):
            if features.momentum == "RISING":
                score += 8
                reasons.append("Positive momentum")
            elif features.momentum == "DECLINING":
                score -= 8
                reasons.append("Negative momentum")

        score = max(0, min(score, 100))
        return {
            "score": score,
            # This is a heuristic signal score, not a calibrated probability.
            "probability": None,
            "evidence_available": evidence_available,
            "reasons": reasons,
        }
