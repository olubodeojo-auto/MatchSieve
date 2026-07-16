from core.sentinel_api import SentinelAPI


class H2HService:

    def __init__(self):

        self.api = SentinelAPI()

    def matches(self, home_team_id, away_team_id):

        data = self.api.head_to_head(home_team_id, away_team_id)

        if data is None:
            return []

        return data.get("data", [])

    def summary(self, home_team_id, away_team_id):

        matches = self.matches(home_team_id, away_team_id)

        summary = {

            "played": len(matches),

            "home_wins": 0,

            "away_wins": 0,

            "draws": 0,

            "goals": 0,

            "btts": 0,

            "over25": 0,

            "under25": 0

        }

        return summary