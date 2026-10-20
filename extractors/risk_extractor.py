from extractors.base_extractor import BaseExtractor


class RiskExtractor(BaseExtractor):
    """Measure data coverage and map explicitly normalized statistics."""

    STAT_FIELDS = (
        "home_goal_average", "away_goal_average",
        "home_conceded_average", "away_conceded_average",
        "home_clean_sheet_rate", "away_clean_sheet_rate", "btts_rate",
        "home_shots", "away_shots", "home_sot", "away_sot",
        "home_dangerous_attacks", "away_dangerous_attacks",
        "home_possession", "away_possession",
        "home_corners", "away_corners", "home_cards", "away_cards",
    )

    @staticmethod
    def _number(value):
        if isinstance(value, bool) or value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number

    def extract(self, match, features):
        statistics = match.statistics if isinstance(match.statistics, dict) else {}
        for field in self.STAT_FIELDS:
            value = self._number(statistics.get(field))
            if value is not None:
                setattr(features, field, value)

        features.total_goal_average = (
            features.home_goal_average + features.away_goal_average
        )
        features.total_conceded_average = (
            features.home_conceded_average + features.away_conceded_average
        )
        features.total_shots = features.home_shots + features.away_shots
        features.total_sot = features.home_sot + features.away_sot
        features.total_dangerous_attacks = (
            features.home_dangerous_attacks + features.away_dangerous_attacks
        )

        xg_available = match.home_xg is not None and match.away_xg is not None
        odds_available = all(value is not None and value > 0 for value in (
            match.home_odds, match.draw_odds, match.away_odds
        ))
        probabilities_available = all(value is not None for value in (
            match.home_probability, match.draw_probability, match.away_probability
        ))
        form_available = bool(features.home_last5 and features.away_last5)
        h2h_available = bool(features.h2h)

        features.data_availability = {
            "fixture_identity": bool(match.fixture_id and match.home_team and match.away_team),
            "xg": xg_available,
            "odds": odds_available,
            "probabilities": probabilities_available,
            "form": form_available,
            "h2h": h2h_available,
            "goal_averages": all(getattr(features, key) is not None for key in (
                "home_goal_average", "away_goal_average"
            )) and all(key in statistics for key in ("home_goal_average", "away_goal_average")),
            "conceded_averages": all(key in statistics and self._number(statistics.get(key)) is not None for key in (
                "home_conceded_average", "away_conceded_average"
            )),
            "clean_sheet_rates": all(key in statistics and self._number(statistics.get(key)) is not None for key in (
                "home_clean_sheet_rate", "away_clean_sheet_rate"
            )),
            "btts_rate": "btts_rate" in statistics and self._number(statistics.get("btts_rate")) is not None,
            "shots": all(key in statistics and self._number(statistics.get(key)) is not None for key in (
                "home_shots", "away_shots", "home_sot", "away_sot"
            )),
        }

        checks = [
            bool(match.fixture_id),
            bool(match.home_team and match.away_team),
            bool(match.league),
            bool(match.kickoff),
            bool(match.status),
            xg_available,
            odds_available,
            probabilities_available,
            form_available,
            h2h_available,
        ]
        features.data_quality = round(sum(checks) / len(checks) * 100)

        # Provider count alone is not evidence that providers agree. Until
        # overlapping fields are explicitly compared, agreement is unknown.
        features.provider_agreement = 0
        return features
