class FeatureEnricher:

    def enrich(self, features):

        # ----------------------------------
        # Goal Statistics
        # ----------------------------------

        self.goal_features(features)

        # ----------------------------------
        # Defence Statistics
        # ----------------------------------

        self.defence_features(features)

        # ----------------------------------
        # Form Statistics
        # ----------------------------------

        self.form_features(features)

        # ----------------------------------
        # Head-to-Head Statistics
        # ----------------------------------

        self.h2h_features(features)

        # ----------------------------------
        # Market Features
        # ----------------------------------

        self.market_features(features)

        # ----------------------------------
        # Performance Features
        # ----------------------------------

        self.performance_features(features)

        # ----------------------------------
        # Advanced Features
        # ----------------------------------

        self.advanced_features(features)

        return features

    # =====================================================
    # GOALS
    # =====================================================

    def goal_features(self, features):

        features.goal_expectancy = round(
            features.home_xg + features.away_xg,
            2
        )

        if features.goal_expectancy >= 3.5:
            features.goal_rating = "Very High"

        elif features.goal_expectancy >= 2.5:
            features.goal_rating = "High"

        elif features.goal_expectancy >= 1.5:
            features.goal_rating = "Medium"

        else:
            features.goal_rating = "Low"

    # =====================================================
    # DEFENCE
    # =====================================================

    def defence_features(self, features):

        features.defence_difference = round(

            abs(

                features.home_defence_strength -

                features.away_defence_strength

            ),

            2

        )

    # =====================================================
    # FORM
    # =====================================================

    def form_features(self, features):

        features.form_difference = abs(

            features.home_form_score -

            features.away_form_score

        )

    # =====================================================
    # HEAD TO HEAD
    # =====================================================

    def h2h_features(self, features):

        features.h2h_strength = len(features.h2h)

    # =====================================================
    # MARKET
    # =====================================================

    def market_features(self, features):

        if features.home_probability > features.away_probability:

            features.favorite = "HOME"

        elif features.away_probability > features.home_probability:

            features.favorite = "AWAY"

        else:

            features.favorite = "DRAW"

        difference = abs(

            features.home_probability -

            features.away_probability

        )

        if difference < 10:

            features.market_balance = "Balanced"

        elif difference < 25:

            features.market_balance = "Competitive"

        else:

            features.market_balance = "One-sided"

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def performance_features(self, features):

        if features.confidence >= 90:

            features.market_confidence = "Very High"

        elif features.confidence >= 75:

            features.market_confidence = "High"

        elif features.confidence >= 60:

            features.market_confidence = "Medium"

        else:

            features.market_confidence = "Low"

    # =====================================================
    # ADVANCED
    # =====================================================

    def advanced_features(self, features):

        features.overall_strength = round(

            (

                features.home_attack_strength +

                features.home_defence_strength +

                features.home_momentum

            ) / 3,

            2

        )