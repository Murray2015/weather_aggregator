from datetime import datetime
import requests
from os import getenv

from .base import WeatherDataClient
from .utils.definitions import weatherbit_wind_direction_lookup, open_weather_visibility_lookup, uv_lookup_codes, weatherbit_weather_code_lookup

# Weatherbit.io
WEATHERBIT_IO_API_KEY = getenv("WEATHERBIT_IO_API_KEY")


class WeatherbitIoClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "http://api.weatherbit.io/v2.0/forecast/hourly"
        self.endpoint = F"?lang=en&key={WEATHERBIT_IO_API_KEY}"

    def get_forecast_lat_lon(self, lat, lon):
        response = requests.get(
            self.base_url + self.endpoint, params={'lat': lat, 'lon': lon})
        return self.process_data(response.json())

    def process_data(self, data: any):
        processed_weather_data = []
        lat = data['lat']
        lon = data['lon']
        place_name = data['city_name']
        for hourly in data['data']:
            processed_data = {
                'lat': lat,
                'lon': lon,
                'place_name': place_name,
                'date_time': datetime.fromisoformat(hourly['timestamp_local']),
                'temperature_celcius': float(hourly['temp']),
                'feels_like_temperature_celcius': float(hourly['app_temp']),
                'wind_speed_kph': float(hourly['wind_spd']),
                'wind_direction': weatherbit_wind_direction_lookup[hourly['wind_cdir_full']],
                'wind_gust_mph': float(hourly['wind_gust_spd']),
                'relative_humidity_percentage': None,
                'visibility': open_weather_visibility_lookup(hourly['vis'] * 1000),
                'uv_index': {'code': hourly['uv'], 'description': uv_lookup_codes[str(int(hourly['uv']))]},
                'weather_type': weatherbit_weather_code_lookup[str(hourly['weather']['code'])],
                'precipitation_probability_percentage': hourly['pop'],
            }
            processed_weather_data.append(processed_data)
        return processed_weather_data


# weatherbit_io = WeatherbitIoClient()
# print('the_rainery get_forecast_lat_lon', weatherbit_io.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('weatherbit_io get_forecast_postcode',
#       weatherbit_io.get_forecast_postcode('GB', 'b17 0hs'))
# print('weatherbit_io get_forecast_city_country',
#       weatherbit_io.get_forecast_city_country("Birmingham", "uk"))
