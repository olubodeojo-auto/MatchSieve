import unittest
from unittest.mock import patch

from services.adapters.footballdata_io_adapter import FootballDataIOAdapter
from services.match_builder import MatchBuilder


class FootballDataIoAdapterAuditTests(unittest.TestCase):
    def test_optional_market_and_xg_fields_may_be_missing(self):
        match = {
            "match_id": 12,
            "home_team": {"team_name": "Home FC"},
            "away_team": {"team_name": "Away FC"},
            "league": {"name": "Test League"},
            "match_date": "2026-10-25T15:00:00Z",
        }
        normalized = FootballDataIOAdapter.convert(match)

        self.assertEqual(normalized.home_team, "Home FC")
        self.assertEqual(normalized.away_team, "Away FC")
        self.assertIsNone(normalized.home_xg)
        self.assertIsNone(normalized.away_xg)
        self.assertIsNone(normalized.home_odds)
        self.assertIsNone(normalized.home_probability)
        self.assertIsNone(normalized.venue)

    def test_missing_team_name_is_reported_as_invalid_fixture(self):
        with self.assertRaisesRegex(ValueError, "team name"):
            FootballDataIOAdapter.convert({
                "home_team": {},
                "away_team": {"team_name": "Away FC"},
            })

    def test_one_malformed_fixture_does_not_abort_the_batch(self):
        builder = MatchBuilder()
        builder.router = type("RouterStub", (), {
            "get_today_matches": lambda _self: {
                "data": {"matches": [
                    {"home_team": {}, "away_team": {"team_name": "Broken FC"}},
                    {
                        "match_id": 2,
                        "home_team": {"team_name": "Home FC"},
                        "away_team": {"team_name": "Away FC"},
                        "league": {"name": "Test League"},
                        "match_date": "2026-10-25T15:00:00Z",
                    },
                ]}
            }
        })()

        with patch("builtins.print"):
            rows = builder.build_today()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].home_team, "Home FC")


if __name__ == "__main__":
    unittest.main()
