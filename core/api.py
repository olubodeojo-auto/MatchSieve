import requests
from pathlib import Path


class SportMonksAPI:

    BASE_URL = "https://api.sportmonks.com/v3/football"

    def __init__(self):
        self.api_key = Path("config/sportmonks_key.txt").read_text().strip()

    def get_fixtures(self):

        url = f"{self.BASE_URL}/fixtures"

        response = requests.get(
            url,
            params={
                "api_token": self.api_key,
                "include": "league;venue;participants;season;round;state"
            }
        )

        response.raise_for_status()

        return response.json()["data"]

    def fixture(self, fixture_id):

        url = f"{self.BASE_URL}/fixtures/{fixture_id}"

        response = requests.get(
            url,
            params={
                "api_token": self.api_key,
                "include": "league;venue;participants;season;round;state"
            }
        )

        response.raise_for_status()

        return response.json()

    def live(self):

        url = f"{self.BASE_URL}/livescores"

        response = requests.get(
            url,
            params={
                "api_token": self.api_key,
                "include": "league;venue;participants;season;round;state"
            }
        )

        response.raise_for_status()

        return response.json()

    def statistics(self, fixture_id):

        url = f"{self.BASE_URL}/fixtures/{fixture_id}"

        response = requests.get(
            url,
            params={
                "api_token": self.api_key,
                "include": "statistics.type"
            }
        )

        response.raise_for_status()

        return response.json()

    def team_matches(self, team_id):

        url = f"{self.BASE_URL}/teams/{team_id}"

        response = requests.get(
            url,
            params={
                "api_token": self.api_key,
                "include": "latest.fixtures"
            }
        )

        response.raise_for_status()

        return response.json()

    def head_to_head(self, team1, team2):

        url = f"{self.BASE_URL}/fixtures/head-to-head/{team1}/{team2}"

        response = requests.get(
            url,
            params={
                "api_token": self.api_key
            }
        )

        response.raise_for_status()

        return response.json()