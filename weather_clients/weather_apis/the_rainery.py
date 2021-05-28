import json
from datetime import datetime
from os import getenv

from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat

from .base import WeatherDataClient
from .utils.definitions import open_weather_wind_direction_lookup, open_weather_visibility_lookup

# The rainery
THE_RAINERY_API_KEY = getenv("THE_RAINERY_API_KEY")


class TheRaineryClient(WeatherDataClient):
    def __init__(self):
        self.headers = {'x-api-key': THE_RAINERY_API_KEY}
        self.base_url = 'https://api.therainery.com/forecast/weather'

    async def get_forecast_lat_lon(self, lat, lon):
        http_client = AsyncHTTPClient()

        response = await http_client.fetch(url_concat(self.base_url, {'latitude': lat, 'longitude': lon}), headers=self.headers)
        raw_data = json.loads(response.body)
        return self.process_data(raw_data)

    def process_data(self, data: any):
        processed_weather_data = []
        lat = data['meta']['latitude']
        lon = data['meta']['longitude']
        place_name = None
        for hourly in data['data']:
            processed_data = {
                'lat': lat,
                'lon': lon,
                'place_name': place_name,
                'date_time': datetime.fromtimestamp(hourly['timestamp']),
                'temperature_celcius': float(hourly['airTemperature']),
                'feels_like_temperature_celcius': None,
                'wind_speed_kph': float(hourly['windSpeed']),
                'wind_direction': open_weather_wind_direction_lookup(hourly['windDirection']),
                'wind_gust_mph': float(hourly['gust']),
                'relative_humidity_percentage': float(hourly['relativeHumidity']),
                'visibility': open_weather_visibility_lookup(hourly['horizontalVisibility']),
                'uv_index': None,
                'weather_type': None,
                'precipitation_probability_percentage': None,
            }
            processed_weather_data.append(processed_data)
        return processed_weather_data


# the_rainery = TheRaineryClient()
# print('the_rainery get_forecast_lat_lon', the_rainery.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('the_rainery get_forecast_postcode',
#       the_rainery.get_forecast_postcode('GB', 'b17 0hs'))
# print('the_rainery get_forecast_city_country',
#       the_rainery.get_forecast_city_country("Birmingham", "uk"))
