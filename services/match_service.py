from core.sentinel_api import SentinelAPI
from models.match import Match


class MatchService:

    def __init__(self):

        self.api = SentinelAPI()

    def get_match(self, fixture_id):

        details = self.api.fixture(fixture_id)

        if details is None:
            return None

        data = details["data"]

        home_team = "Unknown"
        away_team = "Unknown"

        home_team_id = None
        away_team_id = None

        participants = data.get("participants", [])

        for participant in participants:

            location = participant.get("meta", {}).get("location")

            if location == "home":

                home_team = participant.get("name")

                home_team_id = participant.get("id")

            elif location == "away":

                away_team = participant.get("name")

                away_team_id = participant.get("id")

        return Match(

            fixture_id=data.get("id"),

            home_team=home_team,
            away_team=away_team,

            home_team_id=home_team_id,
            away_team_id=away_team_id,

            league=data.get("league", {}).get("name", "Unknown"),
            league_id=data.get("league_id"),

            venue=data.get("venue", {}).get("name", "Unknown"),
            venue_id=data.get("venue_id"),

            kickoff=data.get("starting_at"),

            status=data.get("state", {}).get("state", "Unknown"),

            season=data.get("season", {}).get("name", "Unknown"),
            season_id=data.get("season_id"),

            round_name=data.get("round", {}).get("name", "Unknown"),
            round_id=data.get("round_id")

        )