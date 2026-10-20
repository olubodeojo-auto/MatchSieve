from extractors.base_extractor import BaseExtractor


class RiskExtractor(BaseExtractor):
    """Estimate data coverage without inventing quality or agreement."""

    def extract(self, match, features):
        xg_available = match.home_xg is not None and match.away_xg is not None
        odds_available = all(value is not None and value > 0 for value in (
            match.home_odds, match.draw_odds, match.away_odds
        ))
        probabilities_available = all(value is not None for value in (
            match.home_probability, match.draw_probability, match.away_probability
        ))
        form_available = bool(match.home_form and match.away_form)
        h2h_available = bool(match.h2h)
        statistics = match.statistics if isinstance(match.statistics, dict) else {}

        features.data_availability = {
            "fixture_identity": bool(match.fixture_id and match.home_team and match.away_team),
            "xg": xg_available,
            "odds": odds_available,
            "probabilities": probabilities_available,
            "form": form_available,
            "h2h": h2h_available,
            "goal_averages": all(statistics.get(key) is not None for key in (
                "home_goal_average", "away_goal_average"
            )),
            "conceded_averages": all(statistics.get(key) is not None for key in (
                "home_conceded_average", "away_conceded_average"
            )),
            "clean_sheet_rates": all(statistics.get(key) is not None for key in (
                "home_clean_sheet_rate", "away_clean_sheet_rate"
            )),
            "btts_rate": statistics.get("btts_rate") is not None,
            "shots": all(statistics.get(key) is not None for key in (
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
