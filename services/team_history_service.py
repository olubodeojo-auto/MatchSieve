from core.sentinel_api import SentinelAPI


class TeamHistoryService:

    def __init__(self):

        self.api = SentinelAPI()

    def last_matches(self, team_id):

        data = self.api.team_matches(team_id)

        if data is None:
            return []

        return (
            data.get("data", {})
                .get("latest", {})
                .get("fixtures", [])
        )

    def summary(self, team_id):

        matches = self.last_matches(team_id)[:10]

        summary = {

            "played": 0,

            "wins": 0,

            "draws": 0,

            "losses": 0,

            "goals_for": 0,

            "goals_against": 0,

            "goal_average": 0,

            "conceded_average": 0,

            "clean_sheets": 0,

            "btts": 0,

            "over25": 0,

            "under25": 0,

            "form_points": 0,

            "weighted_form": 0,

            "momentum": "UNKNOWN",

            "fixtures": matches

        }

        return summary