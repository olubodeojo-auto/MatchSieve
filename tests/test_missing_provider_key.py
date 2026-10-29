from __future__ import annotations

import unittest
from unittest.mock import patch

from providers.footballdata_io import FootballDataIO


class MissingFootballDataIOKeyTests(unittest.TestCase):
    @patch("providers.footballdata_io.Path.read_text", side_effect=FileNotFoundError)
    def test_missing_key_file_does_not_crash_initialization(self, _read_text):
        client = FootballDataIO()
        self.assertEqual(client.api_key, "")

    @patch("providers.footballdata_io.Path.read_text", side_effect=FileNotFoundError)
    @patch("providers.footballdata_io.requests.get")
    def test_missing_key_fails_before_network_request(self, get, _read_text):
        client = FootballDataIO()
        with self.assertRaisesRegex(RuntimeError, "not configured"):
            client.fixtures()
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
