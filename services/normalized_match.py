class NormalizedMatch:

    def __init__(self):

        # Core
        self.fixture_id = None
        self.provider = None

        # Competition
        self.league = None
        self.country = None
        self.season = None
        self.round = None

        # Teams
        self.home_team = None
        self.away_team = None

        self.home_logo = None
        self.away_logo = None

        # Match
        self.kickoff = None
        self.status = None
        self.minute = None

        # Score
        self.home_score = 0
        self.away_score = 0

        # Expected Goals
        self.home_xg = None
        self.away_xg = None

        # Probabilities
        self.home_probability = None
        self.draw_probability = None
        self.away_probability = None

        # Odds
        self.home_odds = None
        self.draw_odds = None
        self.away_odds = None

        # Rankings
        self.home_rank = None
        self.away_rank = None

        self.home_points = None
        self.away_points = None

        # Form
        self.home_form = []
        self.away_form = []

        # Venue & Weather
        self.venue = None
        self.weather = None

        # Statistics
        self.statistics = {}

        # Match Events
        self.events = []

        # Head-to-head
        self.h2h = []

        # Injuries
        self.injuries = []

        # Predictions
        self.predictions = {}

        # News
        self.news = []

        # Bookmakers
        self.bookmakers = []

        # Confidence scores
        self.confidence = {}

        # Providers used
        self.providers = []

        # Raw provider payloads
        self.raw_data = {}

    def add_provider(self, provider):

        if provider not in self.providers:
            self.providers.append(provider)

    def add_raw_data(self, provider, data):

        self.raw_data[provider] = data

    def to_dict(self):

        return self.__dict__