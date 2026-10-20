from extractors.base_extractor import BaseExtractor


class RiskExtractor(BaseExtractor):
    """Estimate data coverage without inventing quality or agreement."""

    def extract(self, match, features):
        checks = [
            bool(match.fixture_id),
            bool(match.home_team and match.away_team),
            bool(match.league),
            bool(match.kickoff),
            bool(match.status),
            match.home_xg is not None and match.away_xg is not None,
            all(value is not None for value in (
                match.home_odds, match.draw_odds, match.away_odds
            )),
            all(value is not None for value in (
                match.home_probability,
                match.draw_probability,
                match.away_probability,
            )),
            bool(match.home_form and match.away_form),
            bool(match.h2h),
        ]

        features.data_quality = round(sum(checks) / len(checks) * 100)

        # Provider count alone is not evidence that providers agree. Until
        # overlapping fields are explicitly compared, agreement is unknown.
        features.provider_agreement = 0

        return features
