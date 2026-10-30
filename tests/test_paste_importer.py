import unittest

from matchsieve.paste_importer import parse_match_history_paste


class MatchHistoryPasteTests(unittest.TestCase):
    def sample(self):
        return "\n".join([
            "Last matches: Le Havre - Home",
            "25.10.2026 | France Ligue 1 | Marseille - Le Havre | 4-3",
            "18.10.2026 | France Ligue 1 | Le Havre - Auxerre | 1-3",
            "Last matches: PSG - Away",
            "17.10.2026 | France Ligue 1 | Strasbourg - PSG | 1-3",
            "14.10.2026 | UEFA Champions League | Manchester City - PSG | 2-4",
            "Head-to-head matches",
            "28.02.2026 | France Ligue 1 | Le Havre - PSG | 0-1",
            "22.11.2025 | France Ligue 1 | PSG - Le Havre | 3-0",
            "Bet9ja odds 1.20 4.50 8.00",
            "Advertisement sponsored bonus",
        ])

    def test_keeps_home_away_and_h2h_separate(self):
        result = parse_match_history_paste(
            self.sample(), home_team="Le Havre", away_team="PSG"
        )
        self.assertEqual(result["sections"]["home_form"][0]["home_team"], "Marseille")
        self.assertEqual(result["sections"]["away_form"][0]["away_team"], "PSG")
        self.assertEqual(result["sections"]["h2h"][0]["home_team"], "Le Havre")
        self.assertEqual(result["coverage"]["home_form"]["records_found"], 2)
        self.assertEqual(result["coverage"]["away_form"]["records_found"], 2)
        self.assertEqual(result["coverage"]["h2h"]["records_found"], 2)

    def test_preserves_date_competition_score_and_venue_context(self):
        result = parse_match_history_paste(
            self.sample(), home_team="Le Havre", away_team="PSG"
        )
        row = result["sections"]["home_form"][0]
        self.assertEqual(row["date"], "2026-10-25")
        self.assertEqual(row["competition"], "France Ligue 1")
        self.assertEqual((row["home_score"], row["away_score"]), (4, 3))
        self.assertEqual(row["venue_context"], "home")

    def test_odds_and_advertisements_are_not_imported(self):
        result = parse_match_history_paste(
            self.sample(), home_team="Le Havre", away_team="PSG"
        )
        self.assertEqual(result["total_records"], 6)
        self.assertGreaterEqual(result["ignored_noise_lines"], 1)
        self.assertIn("odds", result["excluded_fields"])
        self.assertNotIn("odds", str(result["sections"]).lower())

    def test_does_not_claim_five_or_fewer_records_are_complete(self):
        result = parse_match_history_paste(
            self.sample(), home_team="Le Havre", away_team="PSG"
        )
        for section in ("home_form", "away_form", "h2h"):
            self.assertFalse(result["coverage"][section]["complete_to_target"])
            self.assertEqual(result["coverage"][section]["target"], 35)

    def test_caps_each_section_at_35(self):
        rows = ["Last matches: Le Havre - Home"]
        rows.extend(
            f"{(i % 28) + 1:02d}.01.2025 | League | Team {i} - Opponent {i} | 1-0"
            for i in range(37)
        )
        result = parse_match_history_paste("\n".join(rows), home_team="Le Havre", away_team="PSG")
        self.assertEqual(len(result["sections"]["home_form"]), 35)
        self.assertFalse(result["coverage"]["home_form"]["complete_to_target"] is False)

    def test_conflicting_scores_are_flagged(self):
        text = "\n".join([
            "Last matches: Le Havre - Home",
            "25.10.2026 | League | Marseille - Le Havre | 4-3",
            "Head-to-head matches",
            "25.10.2026 | League | Marseille - Le Havre | 3-3",
        ])
        result = parse_match_history_paste(text, home_team="Le Havre", away_team="PSG")
        self.assertTrue(any("Conflicting scores" in warning for warning in result["errors"]))

    def test_unknown_competition_is_flagged(self):
        text = "Last matches: Le Havre - Home\n25.10.2026 Marseille - Le Havre 4-3"
        result = parse_match_history_paste(text, home_team="Le Havre", away_team="PSG")
        self.assertEqual(result["sections"]["home_form"][0]["competition"], "Unknown competition")
        self.assertTrue(any("competition is not present" in warning for warning in result["errors"]))

    def test_multiline_clipboard_rows_are_supported(self):
        text = "\n".join([
            "Last matches: Le Havre - Home",
            "25.10.2026",
            "L1",
            "Marseille",
            "Marseille",
            "Le Havre",
            "Le Havre",
            "4",
            "3",
            "W",
            "Last matches: PSG - Away",
            "17.10.2026",
            "L1",
            "Strasbourg",
            "Strasbourg",
            "PSG",
            "PSG",
            "1",
            "3",
            "L",
            "Head-to-head matches",
            "28.02.2026",
            "L1",
            "Le Havre",
            "Le Havre",
            "PSG",
            "PSG",
            "0",
            "1",
            "L",
        ])
        result = parse_match_history_paste(text, home_team="Le Havre", away_team="PSG")
        self.assertEqual(result["sections"]["home_form"][0]["home_team"], "Marseille")
        self.assertEqual(result["sections"]["home_form"][0]["competition"], "L1")
        self.assertEqual((result["sections"]["home_form"][0]["home_score"], result["sections"]["home_form"][0]["away_score"]), (4, 3))
        self.assertEqual(result["sections"]["away_form"][0]["away_team"], "PSG")
        self.assertEqual(result["sections"]["h2h"][0]["home_team"], "Le Havre")

    def test_invalid_date_is_not_silently_accepted(self):
        result = parse_match_history_paste(
            "Last matches: Le Havre - Home\n31.02.2026 | League | Home FC - Away FC | 1-0",
            home_team="Le Havre", away_team="PSG",
        )
        self.assertEqual(result["sections"]["home_form"], [])


if __name__ == "__main__":
    unittest.main()
