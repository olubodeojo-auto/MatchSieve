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
        self.assertEqual(mapping["stats"], "https://www.soccerway.com/match/home-id/away-id/summary/stats/?mid=match-1")
        self.assertEqual(mapping["lineups"], "https://www.soccerway.com/match/home-id/away-id/summary/lineups/?mid=match-1")

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


    def test_validate_match_url_accepts_locale_match_route_and_strips_tabs(self):
        value = SoccerwayAdapter.validate_url(
            "https://ng.soccerway.com/match/como-ttyLthOA/manchester-united-ppjDR086/summary/stats/"
        )
        self.assertEqual(
            value,
            "https://ng.soccerway.com/match/como-ttyLthOA/manchester-united-ppjDR086/",
        )

    def test_validate_match_list_url_accepts_locale_home_or_matches(self):
        self.assertEqual(
            SoccerwayAdapter.validate_match_list_url("https://ng.soccerway.com/"),
            "https://ng.soccerway.com/",
        )
        self.assertEqual(
            SoccerwayAdapter.validate_match_list_url("https://ng.soccerway.com/matches/?date=2026-10-21"),
            "https://ng.soccerway.com/matches/?date=2026-10-21",
        )

    def test_validate_match_list_url_rejects_match_detail(self):
        with self.assertRaises(ValueError):
            SoccerwayAdapter.validate_match_list_url(
                "https://ng.soccerway.com/match/home-id/away-id/"
            )

    def test_history_expand_label_recognition(self):
        self.assertEqual(SoccerwayAdapter._label_kind("Show more matches"), "expand_history")
        self.assertEqual(SoccerwayAdapter._label_kind("Last meetings"), "h2h_meetings")
        self.assertEqual(SoccerwayAdapter._label_kind("Last matches"), "team_form")


    def test_history_label_classification_does_not_confuse_team_form_with_direct_h2h(self):
        self.assertEqual(SoccerwayAdapter._label_kind("Last matches"), "team_form")
        self.assertEqual(SoccerwayAdapter._label_kind("Last meetings"), "h2h_meetings")

    def test_fixture_url_recognition_accepts_real_soccerway_team_identifiers(self):
        self.assertTrue(SoccerwayAdapter._is_match_url(
            "https://ng.soccerway.com/match/como-ttyLthOA/manchester-united-ppjDR086/"
        ))


    def test_fixture_parser_keeps_separate_fixtures_and_competition_heading(self):
        class FakeLocator:
            def __init__(self, data=None, text="", attrs=None, descendants=None, ancestors=None):
                self.data = data or []
                self.text = text
                self.attrs = attrs or {}
                self.descendants = descendants or {}
                self.ancestors = ancestors or {}
                self.first = self

            def count(self):
                return len(self.data) if self.data else (1 if self.text or self.attrs else 0)

            def nth(self, i):
                return self.data[i]

            def get_attribute(self, name):
                return self.attrs.get(name)

            def inner_text(self, timeout=None):
                return self.text

            def locator(self, selector):
                if selector.startswith("xpath=ancestor::"):
                    return self.ancestors.get(selector, FakeLocator())
                return self.descendants.get(selector, FakeLocator())

        class FakePage:
            def __init__(self, links):
                self.links = links
            def locator(self, selector):
                if selector == "a[href*='/match/'],a[href*='/game/']":
                    return FakeLocator(self.links)
                return FakeLocator()

        def card(url, label, text, heading="Premier League - Round 9"):
            link = FakeLocator(text=label, attrs={"href": url})
            card_container = FakeLocator(
                text=text,
                descendants={"a[href*='/match/'],a[href*='/game/']": FakeLocator([link]),
                             "a[href*='/team/']": FakeLocator()},
                ancestors={"xpath=ancestor::*[1]": FakeLocator(text=text)},
            )
            # The link has one compact card as its first ancestor.
            link.ancestors["xpath=ancestor::*[1]"] = card_container
            card_container.ancestors["xpath=preceding::*[self::h1 or self::h2 or self::h3 or self::h4 or @role='heading'][1]"] = FakeLocator(text=heading)
            return link

        first = card("/match/alpha-id/beta-id/", "Alpha v Beta", "Premier League - Round 9 17:45 Alpha 2 - 0 Beta")
        second = card("/match/gamma-id/delta-id/", "Gamma v Delta", "Premier League - Round 9 20:00 Gamma - Delta")
        fixtures = SoccerwayAdapter._extract_fixture_rows(
            FakePage([first, second]), "https://ng.soccerway.com/", max_fixtures=10
        )
        self.assertEqual(len(fixtures), 2)
        self.assertEqual([(x["home_team"], x["away_team"]) for x in fixtures],
                         [("Alpha", "Beta"), ("Gamma", "Delta")])
        self.assertEqual(fixtures[0]["competition"], "Premier League - Round 9")
        self.assertEqual(fixtures[0]["score"], {"home": 2, "away": 0})
        self.assertEqual(fixtures[1]["kickoff_display"], "20:00")

    def test_flashscore_mobi_domain_is_not_allowed_for_soccerway_adapter(self):
        with self.assertRaises(ValueError):
            SoccerwayAdapter.validate_match_list_url("https://www.flashscore.mobi/")

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
