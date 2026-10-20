import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from matchsieve.db import initialize
from matchsieve.repository import Repository
from matchsieve.webserver import Handler


class MatchSieveHttpApiTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="matchsieve-http-test-")
        db_path = Path(self.tempdir.name) / "test.sqlite3"
        initialize(db_path)
        Handler.repo = Repository(db_path)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tempdir.cleanup()

    def get_json(self, path):
        with urllib.request.urlopen(self.base + path, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def post_json(self, path, payload):
        request = urllib.request.Request(
            self.base + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_public_customer_read_routes_and_static_assets(self):
        status, value = self.get_json("/api/status")
        self.assertEqual(200, status)
        self.assertEqual("MatchSieve", value["product"])
        self.assertFalse(value["production_ready"])
        for path in ("/api/mobile/fixtures", "/api/mobile/markets", "/api/mobile/research/history", "/api/providers"):
            status, _ = self.get_json(path)
            self.assertEqual(200, status, path)
        with urllib.request.urlopen(self.base + "/", timeout=3) as response:
            self.assertEqual(200, response.status)
            self.assertIn(b"MatchSieve", response.read())
        with urllib.request.urlopen(self.base + "/app.js", timeout=3) as response:
            self.assertEqual(200, response.status)

    def test_mobile_fixture_to_report_history_and_detail(self):
        status, created = self.post_json("/api/fixture", {
            "competition": "Synthetic Test League",
            "season": "2026",
            "kickoff_utc": "2026-10-25T15:00:00Z",
            "home_team": "Synthetic Home FC",
            "away_team": "Synthetic Away FC",
            "status": "scheduled",
            "source_key": "manual_test",
            "source_ref": "synthetic unit test only",
        })
        self.assertEqual(201, status)
        fixture_id = created["fixture_id"]
        with patch("matchsieve.kb_writer.refresh_indexes", return_value={}):
            status, report = self.post_json("/api/mobile/research", {
                "fixture_id": fixture_id,
                "market": "UNDER_4_5",
                "ollama": False,
            })
        self.assertEqual(200, status)
        self.assertEqual("LIMITED_EVIDENCE", report["status"])
        self.assertEqual(fixture_id, report["fixture"]["id"])
        report_id = report["report_id"]
        self.assertGreater(report_id, 0)

        status, history = self.get_json("/api/mobile/research/history")
        self.assertEqual(200, status)
        self.assertEqual(report_id, history[0]["report_id"])
        status, detail = self.get_json(f"/api/mobile/research/{report_id}")
        self.assertEqual(200, status)
        self.assertEqual(report_id, detail["report_id"])
        self.assertEqual(fixture_id, detail["fixture"]["id"])

    def test_disabled_provider_is_rejected_without_network_fanout(self):
        request = urllib.request.Request(
            self.base + "/api/provider-fetch",
            data=json.dumps({"provider": "sportscore", "date": "2026-10-25"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(409, caught.exception.code)
        payload = json.loads(caught.exception.read().decode("utf-8"))
        self.assertEqual("failed", payload["status"])
        self.assertIn("not enabled", payload["message"])

    def test_malformed_json_is_a_400_not_a_server_crash(self):
        request = urllib.request.Request(
            self.base + "/api/mobile/research",
            data=b"{bad json",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(400, caught.exception.code)
        payload = json.loads(caught.exception.read().decode("utf-8"))
        self.assertIn("error", payload)


if __name__ == "__main__":
    unittest.main()
