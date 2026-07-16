from providers.footballdata_io import FootballDataIO
from providers.football_data_org import FootballDataAPI
from providers.livefootball_provider import LiveFootballProvider
from providers.sportscore_provider import SportScoreProvider
from providers.clearsports_provider import ClearSportsProvider
from providers.openweather_provider import OpenWeatherProvider


class ProviderRouter:

    def __init__(self):

        self.footballdata = FootballDataIO()
        self.footballdataorg = FootballDataAPI()
        self.livefootball = LiveFootballProvider()
        self.sportscore = SportScoreProvider()
        self.clearsports = ClearSportsProvider()
        self.weather = OpenWeatherProvider()

    def get_today_matches(self):

        try:
            return self.footballdata.fixtures()
        except Exception as e:
            print(f"FootballData.io error: {e}")
            return None

    def get_live_matches(self):

        try:
            return self.livefootball.fixtures()
        except Exception as e:
            print(f"LiveFootball error: {e}")
            return None

    def get_competitions(self):

        try:
            return self.footballdataorg.competitions()
        except Exception as e:
            print(f"Football-Data.org error: {e}")
            return None

    def get_news(self):

        try:
            return self.clearsports.news()
        except Exception as e:
            print(f"ClearSports error: {e}")
            return None

    def get_weather(self, city):

        try:
            return self.weather.current(city)
        except Exception as e:
            print(f"Weather error: {e}")
            return None