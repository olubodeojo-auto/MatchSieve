from engines.base_engine import BaseEngine


class NBSEngine(BaseEngine):

    def __init__(self):
        super().__init__("NBS Engine")

    def calculate(self, match):

        score = 0
        reasons = []

        if match.home_team != "Unknown":
            score += 15
            reasons.append("Home team identified")

        if match.away_team != "Unknown":
            score += 15
            reasons.append("Away team identified")

        if match.league != "Unknown":
            score += 20
            reasons.append("League identified")

        if match.venue != "Unknown":
            score += 10
            reasons.append("Venue identified")

        if match.status in ["NS", "LIVE", "HT", "1H", "2H"]:
            score += 20
            reasons.append("Match state supported")

        if match.season != "Unknown":
            score += 20
            reasons.append("Season identified")

        score = min(score, 100)

        if score >= 85:
            risk = "LOW"
        elif score >= 65:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "score": score,
            "risk": risk,
            "reasons": reasons
        }