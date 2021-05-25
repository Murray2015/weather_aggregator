import requests
from datetime import datetime
from os import getenv

from .base import WeatherDataClient
from .utils.definitions import open_weather_wind_direction_lookup, open_weather_visibility_lookup, tomorrow_io_weather_code_lookup


# Tomorrow.io
TOMORROW_API_KEY = getenv("TOMORROW_API_KEY")


class TomorrowIOClient(WeatherDataClient):
    def __init__(self):
        self.base_url = f'https://api.tomorrow.io/v4/timelines'
        self.params = {
            'fields': 'temperature,precipitationIntensity,precipitationType,windSpeed,windGust,windDirection,temperature,temperatureApparent,cloudCover,cloudBase,cloudCeiling,humidity,visibility,weatherCode,precipitationProbability', 'timesteps': '1h',
            'units': 'metric',
            'apikey': TOMORROW_API_KEY
        }

    def get_forecast_lat_lon(self, lat, lon):
        params = {**self.params, 'location': f"{lat},{lon}"}
        response = requests.get(self.base_url, params=params)
        raw_data = response.json()
        return self.process_data(raw_data, lat, lon)

    def process_data(self, data, lat, lon):
        processed_weather_data = []
        place_name = None
        for hourly in data['data']['timelines'][0]['intervals']:
            processed_data = {
                'lat': lat,
                'lon': lon,
                'place_name': place_name,
                'date_time': datetime.strptime(hourly['startTime'], '%Y-%m-%dT%H:%M:%S%z'),
                'temperature_celcius': float(hourly['values']['temperature']),
                'feels_like_temperature_celcius': float(hourly['values']['temperatureApparent']),
                'wind_speed_kph': float(hourly['values']['windSpeed']),
                'wind_direction': open_weather_wind_direction_lookup(hourly['values']['windDirection']),
                'wind_gust_mph': float(hourly['values']['windGust']),
                'relative_humidity_percentage': float(hourly['values']['humidity']),
                'visibility': open_weather_visibility_lookup(hourly['values']['visibility']),
                'uv_index': None,
                'weather_type': tomorrow_io_weather_code_lookup[hourly['values']['weatherCode']],
                'precipitation_probability_percentage': float(hourly['values']['precipitationProbability']),
            }
            processed_weather_data.append(processed_data)
        return processed_weather_data


# tomorrow_io = TomorrowIOClient()
# print('tomorrow_io get_forecast_lat_lon', tomorrow_io.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('tomorrow_io get_forecast_postcode',
#       tomorrow_io.get_forecast_postcode('GB', 'b17 0hs'))
# print('tomorrow_io get_forecast_city_country',
#       tomorrow_io.get_forecast_city_country("Birmingham", "uk"))
