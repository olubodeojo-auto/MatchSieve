import requests
from pathlib import Path


class OddsProvider:

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):

        self.api_key = Path(
            "config/theodds_key.txt"
        ).read_text().strip()

    def sports(self):

        url = f"{self.BASE_URL}/sports"

        response = requests.get(

            url,

            params={

                "apiKey": self.api_key

            }

        )

        return response.json()