class Match:

    def __init__(
        self,
        fixture_id,
        home_team,
        away_team,
        league,
        venue,
        kickoff,
        status,
        season,
        round_name,

        # IDs
        home_team_id=None,
        away_team_id=None,
        league_id=None,
        season_id=None,
        venue_id=None,
        round_id=None
    ):

        # Match
        self.fixture_id = fixture_id
        self.kickoff = kickoff
        self.status = status

        # Teams
        self.home_team = home_team
        self.away_team = away_team

        # IDs
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id

        self.league_id = league_id
        self.season_id = season_id
        self.venue_id = venue_id
        self.round_id = round_id

        # Competition
        self.league = league
        self.season = season
        self.round_name = round_name

        # Venue
        self.venue = venue

    def __str__(self):

        return (
            f"{self.home_team} vs {self.away_team}\n"
            f"League : {self.league}\n"
            f"Venue  : {self.venue}\n"
            f"Status : {self.status}\n"
            f"Kickoff: {self.kickoff}"
        )