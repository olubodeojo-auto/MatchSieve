import requests
from pathlib import Path


class OpenWeatherProvider:

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):

        self.api_key = Path(
            "config/openweather_key.txt"
        ).read_text().strip()

    def current(self, latitude, longitude):

        response = requests.get(

            f"{self.BASE_URL}/weather",

            params={

                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"

            }

        )

        response.raise_for_status()

        return response.json()

    def forecast(self, latitude, longitude):

        response = requests.get(

            f"{self.BASE_URL}/forecast",

            params={

                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric"

            }

        )

        response.raise_for_status()

        return response.json()