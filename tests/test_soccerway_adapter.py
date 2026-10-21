from __future__ import annotations

import unittest

from matchsieve.collectors.soccerway import SoccerwayAdapter


class SoccerwayAdapterTests(unittest.TestCase):
    def test_validate_url_accepts_match_and_strips_tabs(self):
        value = SoccerwayAdapter.validate_url(
            "https://ng.soccerway.com/match/croatia-id/england-id/summary/lineups/?mid=abc"
        )
        self.assertEqual(
            value,
            "https://ng.soccerway.com/match/croatia-id/england-id/?mid=abc",
        )

    def test_validate_url_rejects_non_soccerway_host(self):
        with self.assertRaises(ValueError):
            SoccerwayAdapter.validate_url("https://example.com/match/home-id/away-id/")

    def test_validate_url_rejects_non_match_pages(self):
        with self.assertRaises(ValueError):
            SoccerwayAdapter.validate_url("https://www.soccerway.com/competition/england/")

    def test_discovery_keeps_same_match_tabs_and_excludes_other_match_and_external_links(self):
        base = "https://www.soccerway.com/match/home-id/away-id/?mid=match-1"
        anchors = [
            {"label": "Stats", "href": "/match/home-id/away-id/summary/stats/?mid=match-1"},
            {"label": "Lineups", "href": "/match/home-id/away-id/summary/lineups/?mid=match-1"},
            {"label": "Different match", "href": "/match/other-home/other-away/summary/stats/"},
            {"label": "External", "href": "https://example.org/match/home-id/away-id/summary/stats/"},
        ]
        found = SoccerwayAdapter.discover_page_urls(base, anchors)
        mapping = {x["page_type"]: x["url"] for x in found}
        self.assertIn("stats", mapping)
        self.assertIn("lineups", mapping)
        self.assertNotIn("different match", mapping)
        self.assertTrue(all("example.org" not in item["url"] for item in found))
        self.assertTrue(all("/match/home-id/away-id/" in item["url"] for item in found))

    def test_title_parser_extracts_teams_without_claiming_a_score(self):
        self.assertEqual(
            SoccerwayAdapter._teams_from_title("Croatia v England 03/10/2026 Lineups | Soccerway"),
            ("Croatia", "England"),
        )

    def test_stats_parser_preserves_source_values_without_numeric_guessing(self):
        result = SoccerwayAdapter._stats_from_rows([
            {"cells": ["Expected goals (xG)", "2.98", "1.36"], "text": "Expected goals (xG) | 2.98 | 1.36"},
            {"cells": ["50%", "Ball possession", "50%"], "text": "50% | Ball possession | 50%"},
            {"cells": ["7", "3", "Shots on target"], "text": "7 | 3 | Shots on target"},
            {"cells": ["Unknown metric", "1", "2"], "text": "Unknown metric | 1 | 2"},
        ])
        self.assertEqual(result["xg"]["home"], "2.98")
        self.assertEqual(result["xg"]["away"], "1.36")
        self.assertEqual(result["possession"]["home"], "50%")
        self.assertEqual(result["shots_on_target"]["home"], "7")
        self.assertEqual(result["shots_on_target"]["away"], "3")
        self.assertNotIn("unknown_metric", result)

    def test_page_limit_is_bounded(self):
        self.assertEqual(SoccerwayAdapter(max_pages=500).max_pages, 9)
        self.assertEqual(SoccerwayAdapter(max_pages=0).max_pages, 1)

    def test_aggregate_keeps_zero_zero_score_and_time_basis_explicit(self):
        pages = [{
            "page_type": "summary",
            "title": "Alpha v Beta | Soccerway",
            "headings": ["Alpha v Beta"],
            "text": "League Match",
            "dom_fields": {
                "home_team": [{"value": "Alpha", "selector": "[data-testid*='home-team' i]"}],
                "away_team": [{"value": "Beta", "selector": "[data-testid*='away-team' i]"}],
                "competition": [{"value": "Premier Division", "selector": "a[href*='/competition/']"}],
                "kickoff": [{"value": "2026-10-21T14:00:00+01:00", "selector": "time[datetime]"}],
                "score": [{"value": "0 - 0", "selector": "[class*='score' i]"}],
                "venue": [{"value": "North Ground", "selector": "[class*='venue' i]"}],
            },
            "table_rows": [],
            "statistics": {},
            "players": [],
            "events": [],
            "json_ld": [],
        }]
        result = SoccerwayAdapter._aggregate(pages, "https://www.soccerway.com/match/alpha-id/beta-id/")
        self.assertEqual(result["match"]["home_team"], "Alpha")
        self.assertEqual(result["match"]["away_team"], "Beta")
        self.assertEqual(result["match"]["home_score"], 0)
        self.assertEqual(result["match"]["away_score"], 0)
        self.assertEqual(result["match"]["kickoff"], "2026-10-21T14:00:00+01:00")
        self.assertIn("timezone not confirmed", result["match"]["kickoff_time_basis"])


if __name__ == "__main__":
    unittest.main()
