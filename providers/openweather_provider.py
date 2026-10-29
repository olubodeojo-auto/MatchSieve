import requests
from pathlib import Path


class OpenWeatherProvider:
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    KEY_PATH = Path("config/openweather_key.txt")

    def __init__(self):
        try:
            self.api_key = self.KEY_PATH.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            self.api_key = ""

    def _require_key(self):
        if not self.api_key:
            raise RuntimeError(
                "OpenWeather is not configured: add the API key to "
                "config/openweather_key.txt before requesting this provider."
            )

    def current(self, latitude, longitude):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/weather",
            params={
                "lat": latitude, "lon": longitude,
                "appid": self.api_key, "units": "metric",
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def forecast(self, latitude, longitude):
        self._require_key()
        response = requests.get(
            f"{self.BASE_URL}/forecast",
            params={
                "lat": latitude, "lon": longitude,
                "appid": self.api_key, "units": "metric",
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
