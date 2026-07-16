from providers.provider_manager import ProviderManager


class SentinelAPI:

    def __init__(self):
        self.provider = ProviderManager()

    def fixtures(self):
        return self.provider.fixtures()

    def fixture(self, fixture_id):
        return self.provider.fixture(fixture_id)

    def live(self):
        return self.provider.live()

    def statistics(self, fixture_id):
        return self.provider.statistics(fixture_id)