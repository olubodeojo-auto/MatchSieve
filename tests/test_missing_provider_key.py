from __future__ import annotations

import unittest
from unittest.mock import patch

from providers.clearsports_provider import ClearSportsProvider
from providers.footballdata_io import FootballDataIO
from providers.football_data_org import FootballDataAPI
from providers.livefootball_provider import LiveFootballProvider
from providers.openweather_provider import OpenWeatherProvider


class MissingProviderKeyTests(unittest.TestCase):
    def test_missing_key_files_do_not_crash_provider_initialization(self):
        with patch("pathlib.Path.read_text", side_effect=FileNotFoundError):
            adapters = [
                FootballDataIO(),
                FootballDataAPI(),
                LiveFootballProvider(),
                ClearSportsProvider(),
                OpenWeatherProvider(),
            ]
        self.assertTrue(all(adapter.api_key == "" for adapter in adapters))

    def test_missing_key_fails_before_network_request(self):
        checks = [
            (FootballDataIO, "fixtures", "providers.footballdata_io.requests.get", ()),
            (FootballDataAPI, "competitions", "providers.football_data_org.requests.get", ()),
            (LiveFootballProvider, "fixtures", "providers.livefootball_provider.requests.get", ()),
            (ClearSportsProvider, "news", "providers.clearsports_provider.requests.get", ()),
            (OpenWeatherProvider, "current", "providers.openweather_provider.requests.get", (1.0, 2.0)),
        ]
        with patch("pathlib.Path.read_text", side_effect=FileNotFoundError):
            adapters = [(adapter_type(), method_name, get_path, args)
                        for adapter_type, method_name, get_path, args in checks]
        for adapter, method_name, get_path, args in adapters:
            with self.subTest(provider=type(adapter).__name__):
                with patch(get_path) as get:
                    with self.assertRaisesRegex(RuntimeError, "not configured"):
                        getattr(adapter, method_name)(*args)
                    get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
