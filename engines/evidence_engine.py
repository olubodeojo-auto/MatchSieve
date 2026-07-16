from engines.base_engine import BaseEngine


class EvidenceEngine(BaseEngine):

    def __init__(self):
        super().__init__("Evidence Engine")

    def calculate(self, context):

        evidence = []
        contradictions = []

        features = context.features
        results = context.results

        over_score = 0
        under_score = 0
        btts_score = 0
        nbs_score = 0

        # -----------------------------
        # Goal Probability
        # -----------------------------

        goal = results.get("Goal Probability Engine")

        if goal:

            score = goal.get("score", 50)

            if score >= 85:
                evidence.append("Elite Goal Probability")
                over_score += 20
                btts_score += 12

            elif score >= 70:
                evidence.append("High Goal Probability")
                over_score += 15
                btts_score += 8

            elif score <= 30:
                evidence.append("Very Low Goal Probability")
                under_score += 18
                nbs_score += 12

            elif score <= 45:
                evidence.append("Low Goal Probability")
                under_score += 10

        # -----------------------------
        # Form Engine
        # -----------------------------

        form = results.get("Form Engine")

        if form:

            rating = form.get("rating", "")

            evidence.append(rating)

            if "Strong" in rating:
                over_score += 5

            if "Poor" in rating:
                under_score += 4

        # -----------------------------
        # NBS Engine
        # -----------------------------

        nbs = results.get("NBS Engine")

        if nbs:

            risk = nbs.get("risk")

            if risk == "LOW":
                evidence.append("Low NBS Risk")

            elif risk == "HIGH":
                evidence.append("High NBS Risk")
                nbs_score += 20
                under_score += 10

            else:
                contradictions.append("Medium NBS Risk")

        # -----------------------------
        # Market
        # -----------------------------

        if features.market_stability == "VOLATILE":

            contradictions.append("Market Volatility")

            over_score -= 4
            under_score -= 4

        if features.market_stability == "STABLE":

            evidence.append("Stable Betting Market")

        # -----------------------------
        # Contradictions
        # -----------------------------

        if over_score >= 15 and under_score >= 15:
            contradictions.append("Over and Under conflict")

        if btts_score >= 10 and nbs_score >= 10:
            contradictions.append("BTTS conflicts with NBS")

        # -----------------------------
        # Confidence
        # -----------------------------

        confidence = 50

        confidence += len(evidence) * 5
        confidence -= len(contradictions) * 8

        confidence = max(5, min(100, confidence))

        return {

            "evidence": evidence,

            "contradictions": contradictions,

            "scores": {

                "OVER": over_score,

                "UNDER": under_score,

                "BTTS": btts_score,

                "NBS": nbs_score

            },

            "confidence": confidence

        }