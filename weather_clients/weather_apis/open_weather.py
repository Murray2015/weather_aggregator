import requests
from datetime import datetime
from os import getenv

from .base import WeatherDataClient
from .utils.definitions import no_data_value, open_weather_visibility_lookup, open_weather_wind_direction_lookup, uv_lookup_codes, no_data_value

# Open Weather
OPEN_WEATHER_API_KEY = getenv("OPEN_WEATHER_API_KEY")


class OpenWeatherClient(WeatherDataClient):
    """ Openweather API client class """

    def __init__(self):
        self.exclude = "minutely"
        self.base_url = f"https://api.openweathermap.org/data/2.5/onecall"

    def process_data(self, raw_data):
        data = []
        lat = raw_data['lat']
        lon = raw_data['lon']
        # Possibly use met office for this? Need a common set of names...
        place_name = None
        for hourly in [raw_data['current'], *raw_data['hourly']]:
            processed_data = {
                'lat': lat,
                'lon': lon,
                'place_name': place_name,
                'date_time': datetime.fromtimestamp(hourly['dt']),
                'temperature_celcius': float(hourly['temp']),
                'feels_like_temperature_celcius': float(hourly['feels_like']),
                'wind_gust_mph': float(hourly.get('wind_gust', no_data_value)),
                'relative_humidity_percentage': float(hourly['humidity']),
                'visibility': open_weather_visibility_lookup(hourly['visibility']),
                'wind_direction': open_weather_wind_direction_lookup(hourly['wind_deg']),
                'wind_speed_mph': float(hourly['wind_speed']),
                'uv_index': {'code': hourly['uvi'], 'description': uv_lookup_codes[str(int(hourly['uvi']))]},
                'weather_type': hourly['weather'][0]['description'],
                'precipitation_probability_percentage': float(hourly.get('pop', no_data_value)),
            }
            data.append(processed_data)
        return data

    def get_forecast_lat_lon(self, lat, lon):
        params = {
            'lat': lat,
            'lon': lon,
            'exclude': self.exclude,
            'appid': OPEN_WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(self.base_url, params=params)
        data = self.process_data(response.json())
        return data


# open_weather = OpenWeatherClient()
# print('get_forecast_lat_lon', open_weather.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('get_forecast_postcode',
#       open_weather.get_forecast_postcode('GB', 'b17 0hs'))
# print('get_forecast_city_country',
#       open_weather.get_forecast_city_country("Birmingham", "uk"))
