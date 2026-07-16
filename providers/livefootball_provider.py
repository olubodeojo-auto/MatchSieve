import requests
from pathlib import Path


class LiveFootballProvider:

    BASE_URL = "https://live-football-api.com/api/v1"

    def __init__(self):

        self.api_key = Path(
            "config/livefootball_key.txt"
        ).read_text().strip()

    def fixtures(self, date=None):

        params = {
            "api_key": self.api_key
        }

        if date:
            params["date"] = date

        response = requests.get(
            f"{self.BASE_URL}/matches",
            params=params
        )

        response.raise_for_status()

        return response.json()

    def live_match_details(self, match_id):

        response = requests.get(

            f"{self.BASE_URL}/live_match_details",

            params={
                "api_key": self.api_key,
                "match_id": match_id
            }

        )

        response.raise_for_status()

        return response.json()

    def lineups(self, match_id):

        response = requests.get(

            f"{self.BASE_URL}/lineups",

            params={
                "api_key": self.api_key,
                "match_id": match_id
            }

        )

        response.raise_for_status()

        return response.json()

    def h2h(self, match_id):

        response = requests.get(

            f"{self.BASE_URL}/h2h",

            params={
                "api_key": self.api_key,
                "match_id": match_id
            }

        )

        response.raise_for_status()

        return response.json()

    def injuries(self, match_id):

        response = requests.get(

            f"{self.BASE_URL}/injuries",

            params={
                "api_key": self.api_key,
                "match_id": match_id
            }

        )

        response.raise_for_status()

        return response.json()

    def leagues(self):

        response = requests.get(

            f"{self.BASE_URL}/leagues",

            params={
                "api_key": self.api_key
            }

        )

        response.raise_for_status()

        return response.json()