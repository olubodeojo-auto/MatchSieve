from providers.openweather_provider import OpenWeatherProvider

weather = OpenWeatherProvider()

# London coordinates for testing
result = weather.current(51.5074, -0.1278)

print(result)