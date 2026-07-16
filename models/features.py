class Features:

    def __init__(self):

        # ==================================================
        # MATCH INFORMATION
        # ==================================================

        self.fixture_id = None

        self.home_team = None
        self.away_team = None

        self.home_team_id = None
        self.away_team_id = None

        self.league = None
        self.league_id = None

        self.season = None
        self.season_id = None

        self.venue = None
        self.venue_id = None

        self.round_name = None
        self.round_id = None

        self.kickoff = None
        self.status = None

        # ==================================================
        # RECENT FORM
        # ==================================================

        self.home_last5 = []
        self.away_last5 = []

        self.home_last10 = []
        self.away_last10 = []

        self.home_form_points = 0
        self.away_form_points = 0

        self.home_weighted_form = 0
        self.away_weighted_form = 0

        # ==================================================
        # HEAD TO HEAD
        # ==================================================

        self.h2h = {}

        self.h2h_played = 0
        self.h2h_home_wins = 0
        self.h2h_away_wins = 0
        self.h2h_draws = 0

        # ==================================================
        # GOALS
        # ==================================================

        self.home_goal_average = 0.0
        self.away_goal_average = 0.0
        self.total_goal_average = 0.0

        # ==================================================
        # DEFENCE
        # ==================================================

        self.home_conceded_average = 0.0
        self.away_conceded_average = 0.0
        self.total_conceded_average = 0.0

        # ==================================================
        # CLEAN SHEETS
        # ==================================================

        self.home_clean_sheet_rate = 0.0
        self.away_clean_sheet_rate = 0.0

        # ==================================================
        # BTTS
        # ==================================================

        self.btts_rate = 0.0

        # ==================================================
        # OVERS
        # ==================================================

        self.over05 = 0.0
        self.over15 = 0.0
        self.over25 = 0.0
        self.over35 = 0.0
        self.over45 = 0.0

        # ==================================================
        # UNDERS
        # ==================================================

        self.under05 = 0.0
        self.under15 = 0.0
        self.under25 = 0.0
        self.under35 = 0.0
        self.under45 = 0.0

        # ==================================================
        # CORNERS
        # ==================================================

        self.home_corners = 0.0
        self.away_corners = 0.0

        # ==================================================
        # CARDS
        # ==================================================

        self.home_cards = 0.0
        self.away_cards = 0.0

        # ==================================================
        # POSSESSION
        # ==================================================

        self.home_possession = 0.0
        self.away_possession = 0.0

        # ==================================================
        # SHOTS
        # ==================================================

        self.home_shots = 0.0
        self.away_shots = 0.0

        self.total_shots = 0.0

        # ==================================================
        # SHOTS ON TARGET
        # ==================================================

        self.home_sot = 0.0
        self.away_sot = 0.0

        self.total_sot = 0.0

        # ==================================================
        # DANGEROUS ATTACKS
        # ==================================================

        self.home_dangerous_attacks = 0.0
        self.away_dangerous_attacks = 0.0

        self.total_dangerous_attacks = 0.0

        # ==================================================
        # xG
        # ==================================================

        self.home_xg = 0.0
        self.away_xg = 0.0

        self.total_xg = 0.0

        # ==================================================
        # RATINGS
        # ==================================================

        self.attack_strength = 0

        self.defence_strength = 0

        self.home_strength = 0

        self.away_strength = 0

        self.momentum = "UNKNOWN"

        self.feature_quality = 100

        # ==================================================
        # MARKET
        # ==================================================

        self.home_odds = None
        self.draw_odds = None
        self.away_odds = None

        # ==================================================
        # AI
        # ==================================================

        self.goal_probability = 0

        self.confidence = 0

        self.market_stability = "UNKNOWN"

        # ==================================================
        # FINAL OUTPUT
        # ==================================================

        self.recommendation = "WAIT"

        self.reason = ""

        self.evidence = []

        self.contradictions = []