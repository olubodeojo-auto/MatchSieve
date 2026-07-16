from providers.odds_provider import OddsProvider


provider = OddsProvider()

sports = provider.sports()

print(sports)