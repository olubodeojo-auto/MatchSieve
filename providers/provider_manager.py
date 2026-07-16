from core.api import SportMonksAPI
from providers.football_data_org import FootballDataAPI
from providers.footballdata_io import FootballDataIO
from providers.livefootball_provider import LiveFootballProvider
from providers.sportscore_provider import SportScoreProvider
from providers.clearsports_provider import ClearSportsProvider
from providers.odds_provider import OddsProvider
from providers.openweather_provider import OpenWeatherProvider


class ProviderManager:

    def __init__(self):

        self.sportmonks = SportMonksAPI()
        self.football_data = FootballDataAPI()
        self.footballdata = FootballDataIO()
        self.livefootball = LiveFootballProvider()
        self.sportscore = SportScoreProvider()
        self.clearsports = ClearSportsProvider()
        self.odds = OddsProvider()
        self.weather = OpenWeatherProvider()

    # --------------------------
    # Football Data
    # --------------------------

    def fixtures(self):

        providers = [

            self.sportmonks,
            self.footballdata,
            self.football_data,
            self.livefootball,
            self.sportscore,
            self.clearsports

        ]

        for provider in providers:

            try:
                data = provider.fixtures()

                if data:
                    return data

            except Exception:
                continue

        return []

    # --------------------------
    # Fixture
    # --------------------------

    def fixture(self, fixture_id):

        providers = [

            self.sportmonks,
            self.footballdata,
            self.livefootball

        ]

        for provider in providers:

            try:

                data = provider.fixture(fixture_id)

                if data:
                    return data

            except Exception:
                continue

        return None

    # --------------------------
    # Live
    # --------------------------

    def live(self):

        providers = [

            self.sportmonks,
            self.livefootball,
            self.sportscore

        ]

        for provider in providers:

            try:

                data = provider.live()

                if data:
                    return data

            except Exception:
                continue

        return []

    # --------------------------
    # Statistics
    # --------------------------

    def statistics(self, fixture_id):

        providers = [

            self.sportmonks,
            self.clearsports,
            self.sportscore

        ]

        for provider in providers:

            try:

                data = provider.statistics(fixture_id)

                if data:
                    return data

            except Exception:
                continue

        return {}

    # --------------------------
    # Odds
    # --------------------------

    def odds(self):

        return self.odds

    # --------------------------
    # Weather
    # --------------------------

    def weather(self):

        return self.weather