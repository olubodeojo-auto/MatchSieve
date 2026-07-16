from engines.base_engine import BaseEngine


class ConfidenceEngine(BaseEngine):

    def __init__(self):
        super().__init__("Confidence Engine")

    def calculate(self, match):

        score = 50

        if match.home_team != "Unknown":
            score += 10

        if match.away_team != "Unknown":
            score += 10

        if match.league != "Unknown":
            score += 10

        if match.venue != "Unknown":
            score += 10

        if match.status != "Unknown":
            score += 10

        return min(score, 100)