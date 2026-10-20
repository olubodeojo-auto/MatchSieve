from engines.base_engine import BaseEngine


class BTTSEngine(BaseEngine):

    def __init__(self):
        super().__init__("BTTS Engine")

    def calculate(self, context):
        features = context.features
        available = getattr(features, "data_availability", {}) or {}
        score = 50
        reasons = []

        if available.get("btts_rate"):
            if features.btts_rate >= 75:
                score += 20
                reasons.append("Excellent BTTS history")
            elif features.btts_rate >= 60:
                score += 10
                reasons.append("Good BTTS history")
            elif features.btts_rate <= 40:
                score -= 15
                reasons.append("Poor BTTS history")

        if available.get("goal_averages"):
            if features.total_goal_average >= 3.0:
                score += 15
                reasons.append("High goal average")
            elif features.total_goal_average <= 2.0:
                score -= 10
                reasons.append("Low goal average")

        if available.get("xg"):
            if features.attack_strength >= 80:
                score += 15
                reasons.append("Strong attacking teams")
            elif features.attack_strength <= 40:
                score -= 10
                reasons.append("Weak attacking teams")

            if features.defence_strength <= 40:
                score += 10
                reasons.append("Weak defensive teams")
            elif features.defence_strength >= 80:
                score -= 10
                reasons.append("Strong defensive teams")

            if features.total_xg >= 2.8:
                score += 10
                reasons.append("High xG")
            elif features.total_xg <= 1.8:
                score -= 8
                reasons.append("Low xG")

        if available.get("form") or available.get("xg"):
            if features.momentum == "RISING":
                score += 8
                reasons.append("Positive momentum")
            elif features.momentum == "DECLINING":
                score -= 8
                reasons.append("Negative momentum")

        score = max(0, min(score, 100))
        evidence_available = any(available.get(key) for key in (
            "btts_rate", "goal_averages", "xg", "form"
        ))

        return {
            "score": score,
            "stars": round(score / 20),
            "yes": evidence_available and score >= 65,
            "no": evidence_available and score < 50,
            "evidence_available": evidence_available,
            "reasons": reasons,
        }
