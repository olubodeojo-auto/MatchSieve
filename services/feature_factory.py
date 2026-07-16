from models.football_features import FootballFeatures


class FeatureFactory:

    def build(self, match):

        features = FootballFeatures()

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        features.fixture_id = match.fixture_id
        features.home_team = match.home_team
        features.away_team = match.away_team

        features.league = match.league
        features.country = match.country

        # --------------------------------------------------
        # Score
        # --------------------------------------------------

        features.home_score = match.home_score
        features.away_score = match.away_score

        # --------------------------------------------------
        # Expected Goals
        # --------------------------------------------------

        features.home_xg = match.home_xg or 0
        features.away_xg = match.away_xg or 0

        # --------------------------------------------------
        # Market
        # --------------------------------------------------

        features.home_probability = match.home_probability or 0
        features.draw_probability = match.draw_probability or 0
        features.away_probability = match.away_probability or 0

        features.home_odds = match.home_odds or 0
        features.draw_odds = match.draw_odds or 0
        features.away_odds = match.away_odds or 0

        # --------------------------------------------------
        # Derived Features
        # --------------------------------------------------

        features.home_attack_strength = self.attack_strength(
            features.home_xg
        )

        features.away_attack_strength = self.attack_strength(
            features.away_xg
        )

        features.home_defence_strength = self.defence_strength(
            features.away_xg
        )

        features.away_defence_strength = self.defence_strength(
            features.home_xg
        )

        features.home_momentum = self.momentum(
            features.home_probability
        )

        features.away_momentum = self.momentum(
            features.away_probability
        )

        features.confidence = self.confidence(
            features
        )

        return features

    # --------------------------------------------------

    def attack_strength(self, xg):

        return round(min(xg * 40, 100), 2)

    # --------------------------------------------------

    def defence_strength(self, opponent_xg):

        return round(max(0, 100 - opponent_xg * 40), 2)

    # --------------------------------------------------

    def momentum(self, probability):

        return round(probability, 2)

    # --------------------------------------------------

    def confidence(self, features):

        score = 0

        if features.home_probability:
            score += 20

        if features.home_odds:
            score += 20

        if features.home_xg:
            score += 20

        if features.league:
            score += 20

        if features.home_team:
            score += 20

        return score