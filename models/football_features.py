class FootballFeatures:

    def __init__(self):

        # =====================================================
        # Match Identity
        # =====================================================

        self.fixture_id = None

        self.home_team = None
        self.away_team = None

        self.league = None
        self.country = None

        # =====================================================
        # Score
        # =====================================================

        self.home_score = 0
        self.away_score = 0

        # =====================================================
        # Expected Goals
        # =====================================================

        self.home_xg = 0
        self.away_xg = 0

        # =====================================================
        # Market
        # =====================================================

        self.home_probability = 0
        self.draw_probability = 0
        self.away_probability = 0

        self.home_odds = 0
        self.draw_odds = 0
        self.away_odds = 0

        # =====================================================
        # Form
        # =====================================================

        self.home_form_score = 0
        self.away_form_score = 0

        # =====================================================
        # Attack
        # =====================================================

        self.home_attack_strength = 0
        self.away_attack_strength = 0

        # =====================================================
        # Defence
        # =====================================================

        self.home_defence_strength = 0
        self.away_defence_strength = 0

        # =====================================================
        # Momentum
        # =====================================================

        self.home_momentum = 0
        self.away_momentum = 0

        # =====================================================
        # League
        # =====================================================

        self.league_strength = 0
        self.league_goal_average = 0
        self.league_btts_rate = 0
        self.league_over25_rate = 0

        # =====================================================
        # Weather
        # =====================================================

        self.weather_factor = 0

        # =====================================================
        # Risk
        # =====================================================

        self.data_quality = 100
        self.provider_agreement = 100
        self.confidence = 0

        # =====================================================
        # H2H
        # =====================================================

        self.h2h = []
        self.h2h_strength = 0

        # =====================================================
        # Goal Intelligence
        # =====================================================

        self.goal_expectancy = 0
        self.goal_rating = ""

        # =====================================================
        # Defence Intelligence
        # =====================================================

        self.defence_difference = 0

        # =====================================================
        # Form Intelligence
        # =====================================================

        self.form_difference = 0

        # =====================================================
        # Market Intelligence
        # =====================================================

        self.favorite = ""

        self.market_balance = ""

        self.market_confidence = ""

        # =====================================================
        # Advanced Intelligence
        # =====================================================

        self.overall_strength = 0

    def to_dict(self):

        return self.__dict__