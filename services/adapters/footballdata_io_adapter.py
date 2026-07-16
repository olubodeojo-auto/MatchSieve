from services.normalized_match import NormalizedMatch


class FootballDataIOAdapter:

    @staticmethod
    def convert(match):

        n = NormalizedMatch()

        n.provider = "FootballData.io"

        n.fixture_id = match["match_id"]

        n.home_team = match["home_team"]["team_name"]
        n.away_team = match["away_team"]["team_name"]

        n.home_logo = match["home_team"]["team_logo"]
        n.away_logo = match["away_team"]["team_logo"]

        n.league = match["league"]["name"]

        n.country = match["league"]["country"]

        n.kickoff = match["match_date"]

        n.home_score = match["score"]["home"]
        n.away_score = match["score"]["away"]

        n.home_xg = match["xg"]["home"]
        n.away_xg = match["xg"]["away"]

        n.home_probability = match["probabilities"]["home_win"]
        n.draw_probability = match["probabilities"]["draw"]
        n.away_probability = match["probabilities"]["away_win"]

        n.home_odds = match["odds"]["home_win"]
        n.draw_odds = match["odds"]["draw"]
        n.away_odds = match["odds"]["away_win"]

        n.venue = match["venue"]["stadium_name"]

        n.add_provider("FootballData.io")

        return n