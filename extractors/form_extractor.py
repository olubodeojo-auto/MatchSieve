from extractors.base_extractor import BaseExtractor


class FormExtractor(BaseExtractor):
    """Convert provider form markers into comparable league points."""

    _RESULT_POINTS = {
        "W": 3, "WIN": 3, "WON": 3,
        "D": 1, "DRAW": 1, "DREW": 1,
        "L": 0, "LOSS": 0, "LOST": 0,
    }

    @classmethod
    def _points(cls, result):
        if isinstance(result, bool):
            return None

        if isinstance(result, (int, float)):
            value = int(result)
            return value if result == value and value in (0, 1, 3) else None

        if isinstance(result, str):
            return cls._RESULT_POINTS.get(result.strip().upper())

        if isinstance(result, dict):
            for key in ("result", "outcome", "status"):
                if key in result:
                    return cls._points(result[key])

        return None

    @classmethod
    def _normalise_form(cls, form):
        if not isinstance(form, (list, tuple)):
            return []
        points = []
        for result in form[-5:]:
            value = cls._points(result)
            if value is not None:
                points.append(value)
        return points

    def extract(self, match, features):
        features.home_last5 = self._normalise_form(match.home_form)
        features.away_last5 = self._normalise_form(match.away_form)

        features.home_form_score = sum(features.home_last5)
        features.away_form_score = sum(features.away_last5)

        # Express recent points on a 0-100 scale (15 points = maximum).
        features.home_weighted_form = round(
            features.home_form_score / 15 * 100, 2
        )
        features.away_weighted_form = round(
            features.away_form_score / 15 * 100, 2
        )

        return features
