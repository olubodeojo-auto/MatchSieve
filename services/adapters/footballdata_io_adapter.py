from services.normalized_match import NormalizedMatch


class FootballDataIOAdapter:
    """Map provider payloads while keeping optional fields genuinely optional."""

    @staticmethod
    def convert(match):
        if not isinstance(match, dict):
            raise ValueError("FootballData.io fixture must be an object")

        home = match.get("home_team") or {}
        away = match.get("away_team") or {}
        league = match.get("league") or {}
        score = match.get("score") or {}
        xg = match.get("xg") or {}
        probabilities = match.get("probabilities") or {}
        odds = match.get("odds") or {}
        venue = match.get("venue") or {}

        home_name = home.get("team_name")
        away_name = away.get("team_name")
        if not home_name or not away_name:
            raise ValueError("FootballData.io fixture is missing a home or away team name")

        n = NormalizedMatch()
        n.provider = "FootballData.io"
        n.fixture_id = match.get("match_id")
        n.home_team = home_name
        n.away_team = away_name
        n.home_logo = home.get("team_logo")
        n.away_logo = away.get("team_logo")
        n.league = league.get("name")
        n.country = league.get("country")
        n.season = match.get("season")
        n.round = match.get("round")
        n.kickoff = match.get("match_date")
        n.status = match.get("status")
        n.minute = match.get("minute")

        # Keep the normalized model's numeric score defaults if the provider
        # has not supplied a score. Optional statistics/markets stay None.
        if score.get("home") is not None:
            n.home_score = score["home"]
        if score.get("away") is not None:
            n.away_score = score["away"]

        n.home_xg = xg.get("home")
        n.away_xg = xg.get("away")
        n.home_probability = probabilities.get("home_win")
        n.draw_probability = probabilities.get("draw")
        n.away_probability = probabilities.get("away_win")
        n.home_odds = odds.get("home_win")
        n.draw_odds = odds.get("draw")
        n.away_odds = odds.get("away_win")
        n.venue = venue.get("stadium_name")

        n.add_provider("FootballData.io")
        return n
