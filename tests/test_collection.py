import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from matchsieve.collection import CollectionCoordinator, SchemaOrgHtmlCollector
from matchsieve.db import table_counts
from matchsieve.agents.data_collection import DataCollectionAgent
from matchsieve.provider_manager import ProviderManager
from matchsieve.repository import Repository


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = Repository(self.root / "archive" / "matchsieve.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def _event_html(self, event=None):
        event = event or {
            "@type": "SportsEvent",
            "@id": "event-123",
            "url": "https://example.test/match/123",
            "name": "Home FC vs Away FC",
            "startDate": "2026-10-25T18:00:00Z",
            "homeTeam": {"@type": "SportsTeam", "name": "Home FC"},
            "awayTeam": {"@type": "SportsTeam", "name": "Away FC"},
            "superEvent": {"@type": "SportsEvent", "name": "Example League"},
            "eventStatus": "https://schema.org/EventCompleted",
            "homeScore": "2",
            "awayScore": "1",
            "additionalProperty": [{"name": "Possession", "value": "55%"}],
        }
        return f'<html><script type="application/ld+json">{json.dumps(event)}</script></html>'

    def test_parser_extracts_structured_fixture_result_and_statistics(self):
        result = SchemaOrgHtmlCollector().parse(self._event_html())

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_collected"], 1)
        record = result["records"][0]
        self.assertEqual(record["home_team"], "Home FC")
        self.assertEqual(record["away_team"], "Away FC")
        self.assertEqual(record["competition"], "Example League")
        self.assertEqual(record["kickoff_utc"], "2026-10-25T18:00:00Z")
        self.assertEqual((record["home_score"], record["away_score"]), (2, 1))
        self.assertEqual(record["status"], "finished")
        self.assertEqual(record["external_id"], "event-123")
        self.assertEqual(record["statistics"][0]["name"], "Possession")

    def test_parser_reports_missing_fields_and_unknown_markup(self):
        missing_away = {
            "@type": "SportsEvent",
            "startDate": "2026-10-25",
            "homeTeam": {"name": "Home FC"},
            "superEvent": {"name": "Example League"},
        }
        result = SchemaOrgHtmlCollector().parse(self._event_html(missing_away))
        self.assertEqual(result["status"], "failed")
        self.assertIn("homeTeam and awayTeam are required", result["errors"][0])

        result = SchemaOrgHtmlCollector().parse("<html><body>Fixture text</body></html>")
        self.assertEqual(result["status"], "failed")
        self.assertIn("No Schema.org SportsEvent", result["errors"][0])

    def test_soccerway_browser_capture_is_blocked_without_network_access(self):
        with self.assertRaisesRegex(PermissionError, "express permission"):
            DataCollectionAgent().collect_soccerway_page("https://www.soccerway.com/")

    def test_saved_html_ingestion_preserves_provenance_and_is_idempotent(self):
        html_path = self.root / "recorded.html"
        html_path.write_text(self._event_html(), encoding="utf-8")
        coordinator = CollectionCoordinator(self.repo)

        first = coordinator.collect_html_file(html_path)
        second = coordinator.collect_html_file(html_path)

        self.assertEqual(first["records_archived"], 1)
        self.assertEqual(second["records_archived"], 1)
        self.assertEqual(table_counts(self.repo.db_path)["fixtures"], 1)
        self.assertEqual(table_counts(self.repo.db_path)["source_snapshots"], 1)
        fixture = self.repo.list_fixtures(limit=1)[0]
        provenance = coordinator.provenance(fixture["id"])
        self.assertEqual(provenance["snapshots"][0]["source_key"], "sports_event_html")
        self.assertEqual(provenance["snapshots"][0]["source_ref"], "event-123")
        self.assertEqual(provenance["snapshots"][0]["source_url"], "https://example.test/match/123")
        self.assertEqual(fixture["home_score"], 2)
        self.assertEqual(coordinator.recent_runs(limit=2)[0]["status"], "success")

    def test_missing_saved_html_is_audited_as_a_collection_failure(self):
        result = CollectionCoordinator(self.repo).collect_html_file(self.root / "missing.html")

        self.assertEqual(result["status"], "failed")
        self.assertIn("FileNotFoundError", result["message"])
        run = CollectionCoordinator(self.repo).recent_runs(limit=1)[0]
        self.assertEqual(run["provider_key"], "sports_event_html")
        self.assertEqual(run["status"], "failed")

    def test_collection_sources_isolates_failures_and_continues(self):
        class FakeProviders:
            def __init__(self):
                self.calls = []

            def fetch(self, provider, **kwargs):
                self.calls.append((provider, kwargs.get("date")))
                if provider == "api_football" and kwargs["date"].endswith("25"):
                    return {"provider": provider, "status": "failed", "records_received": 0, "message": "offline"}
                return {"provider": provider, "status": "success", "records_received": 1, "message": "ok"}

        providers = FakeProviders()
        coordinator = CollectionCoordinator(self.repo, providers=providers)
        result = coordinator.collect_sources(
            ["api_football", "sportscore"],
            date_from="2026-10-25",
            date_to="2026-10-26",
        )

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["sources_requested"], 2)
        self.assertEqual(providers.calls[0], ("api_football", "2026-10-25"))
        self.assertEqual(providers.calls[-1], ("sportscore", "2026-10-26"))
        self.assertEqual(result["results"][0]["status"], "partial")
        self.assertEqual(result["results"][1]["status"], "success")

    def test_provider_responses_are_cached_and_force_refresh_bypasses_cache(self):
        row = {
            "external_id": "score-1",
            "competition": "Example League",
            "kickoff_utc": "2026-10-25T18:00:00Z",
            "home_team": "Home FC",
            "away_team": "Away FC",
            "status": "scheduled",
            "source_url": "https://example.test/",
            "provider_payload": {"fixture": "sample"},
        }
        with (
            patch("matchsieve.provider_manager.ENABLED_PROVIDERS", ["sportscore"]),
            patch("matchsieve.provider_manager.SportScoreProvider.fetch_fixtures", return_value=[row]) as fetch,
            patch("matchsieve.provider_manager.refresh_indexes", return_value={}),
        ):
            manager = ProviderManager(self.repo)
            first = manager.fetch("sportscore", date="2026-10-25")
            cached = manager.fetch("sportscore", date="2026-10-25")
            refreshed = manager.fetch("sportscore", date="2026-10-25", force_refresh=True)

        self.assertFalse(first["cache_hit"])
        self.assertTrue(cached["cache_hit"])
        self.assertFalse(refreshed["cache_hit"])
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(table_counts(self.repo.db_path)["fixtures"], 1)
        self.assertTrue((self.root / "archive" / "cache" / "provider-fetch").is_dir())

    def test_coverage_reports_empty_dates_and_source_provenance(self):
        html_path = self.root / "recorded.html"
        html_path.write_text(self._event_html(), encoding="utf-8")
        coordinator = CollectionCoordinator(self.repo)
        coordinator.collect_html_file(html_path)

        coverage = coordinator.coverage("2026-10-25", "2026-10-26")

        self.assertEqual(coverage["records_collected"], 1)
        self.assertEqual(coverage["days_without_fixtures"], ["2026-10-26"])
        self.assertEqual(coverage["days"][0]["sources"], "sports_event_html")


if __name__ == "__main__":
    unittest.main()
