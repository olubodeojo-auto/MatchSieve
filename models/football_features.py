class FootballFeatures:

    def __init__(self):

        # =====================================================
        # MATCH IDENTITY
        # =====================================================

        self.fixture_id = None

        self.home_team = None
        self.away_team = None

        self.home_team_id = None
        self.away_team_id = None

        self.league = None
        self.country = None
        self.season = None
        self.round = None

        self.venue = None
        self.kickoff = None
        self.status = None
        self.minute = 0

        # =====================================================
        # SCORE
        # =====================================================

        self.home_score = 0
        self.away_score = 0

        # =====================================================
        # FORM
        # =====================================================

        self.home_last5 = []
        self.away_last5 = []

        self.home_last10 = []
        self.away_last10 = []

        self.home_form_score = 0
        self.away_form_score = 0

        self.home_form_points = 0
        self.away_form_points = 0

        self.home_weighted_form = 0
        self.away_weighted_form = 0

        self.form_difference = 0

        # =====================================================
        # GOALS
        # =====================================================

        self.home_goal_average = 0
        self.away_goal_average = 0
        self.total_goal_average = 0

        self.goal_expectancy = 0
        self.goal_probability = 0

        self.goal_rating = ""

        # =====================================================
        # xG
        # =====================================================

        self.home_xg = 0
        self.away_xg = 0

        self.total_xg = 0

        # =====================================================
        # DEFENCE
        # =====================================================

        self.home_conceded_average = 0
        self.away_conceded_average = 0
        self.total_conceded_average = 0

        self.home_clean_sheet_rate = 0
        self.away_clean_sheet_rate = 0

        self.home_defence_strength = 0
        self.away_defence_strength = 0

        self.defence_strength = 0
        self.defence_difference = 0

        # =====================================================
        # ATTACK
        # =====================================================

        self.home_attack_strength = 0
        self.away_attack_strength = 0

        self.attack_strength = 0

        # =====================================================
        # SHOTS
        # =====================================================

        self.home_shots = 0
        self.away_shots = 0

        self.total_shots = 0

        self.home_sot = 0
        self.away_sot = 0

        self.total_sot = 0

        self.home_dangerous_attacks = 0
        self.away_dangerous_attacks = 0

        self.total_dangerous_attacks = 0

        # =====================================================
        # POSSESSION
        # =====================================================

        self.home_possession = 0
        self.away_possession = 0

        # =====================================================
        # CORNERS
        # =====================================================

        self.home_corners = 0
        self.away_corners = 0

        # =====================================================
        # CARDS
        # =====================================================

        self.home_cards = 0
        self.away_cards = 0

        # =====================================================
        # BTTS / OVERS / UNDERS
        # =====================================================

        self.btts_rate = 0

        self.over05 = 0
        self.over15 = 0
        self.over25 = 0
        self.over35 = 0
        self.over45 = 0

        self.under05 = 0
        self.under15 = 0
        self.under25 = 0
        self.under35 = 0
        self.under45 = 0

        # =====================================================
        # MARKET
        # =====================================================

        self.home_probability = 0
        self.draw_probability = 0
        self.away_probability = 0

        self.home_odds = 0
        self.draw_odds = 0
        self.away_odds = 0

        self.favorite = ""

        self.market_balance = ""
        self.market_confidence = ""
        self.market_stability = "UNKNOWN"

        # =====================================================
        # LEAGUE
        # =====================================================

        self.league_strength = 0

        self.league_goal_average = 0
        self.league_btts_rate = 0
        self.league_over25_rate = 0

        # =====================================================
        # WEATHER
        # =====================================================

        self.weather_factor = 0

        # =====================================================
        # H2H
        # =====================================================

        self.h2h = []

        self.h2h_played = 0
        self.h2h_home_wins = 0
        self.h2h_away_wins = 0
        self.h2h_draws = 0

        self.h2h_strength = 0

        # =====================================================
        # MOMENTUM
        # =====================================================

        self.home_momentum = 0
        self.away_momentum = 0

        self.momentum = "UNKNOWN"

        # =====================================================
        # AI
        # =====================================================

        self.overall_strength = 0

        self.value_score = 0

        self.trap_risk = 0
        self.explosion_risk = 0

        # Unknown until the pipeline measures actual coverage.
        self.data_quality = 0
        self.provider_agreement = 0
        self.feature_quality = 0
        self.data_availability = {}

        self.confidence = 0

        self.recommendation = "WAIT"

        # =====================================================
        # EXPLAINABILITY
        # =====================================================

        self.evidence = []
        self.contradictions = []

    def to_dict(self):

        return self.__dict__