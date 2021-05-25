from datetime import datetime
import requests
from os import getenv

from .base import WeatherDataClient
from .utils.definitions import no_data_value, open_weather_wind_direction_lookup, open_weather_visibility_lookup

# Stormglass.io
STORM_GLASS_API_KEY = getenv("STORM_GLASS_API_KEY")


class StormGlassClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "https://api.stormglass.io/v2"
        self.weather_endpoint = "/weather/point"
        self.params = {"params": ','.join(['airTemperature', 'pressure', 'cloudCover', 'gust', 'humidity', 'precipitation', 'swellDirection', 'swellHeight', 'swellPeriod',
                                           'secondarySwellPeriod', 'secondarySwellDirection', 'secondarySwellHeight', 'visibility', 'waterTemperature', 'waveDirection', 'waveHeight', 'wavePeriod', 'windDirection', 'windSpeed'])}
        self.headers = {'Authorization': STORM_GLASS_API_KEY
                        }

    def get_forecast_lat_lon(self, lat, lon):
        response = requests.get(
            self.base_url + self.weather_endpoint, params={**self.params, "lat": lat, "lng": lon}, headers=self.headers)
        temp = response.json()
        return self.process_data(response.json())

    def process_data(self, data: any):
        processed_weather_data = {"dwd": [], "noaa": [], "sg": []}
        lat = data['meta']['lat']
        lon = data['meta']['lng']
        place_name = None
        for hourly in data['hours']:
            for provider in ["dwd", "noaa", "sg"]:
                processed_data = {
                    'lat': lat,
                    'lon': lon,
                    'place_name': place_name,
                    'date_time': datetime.fromisoformat(hourly['time']),
                    'temperature_celcius': float(hourly['airTemperature'].get(provider, no_data_value)),
                    'feels_like_temperature_celcius': None,
                    'wind_speed_kph': float(hourly['windSpeed'].get(provider, no_data_value)),
                    'wind_direction': open_weather_wind_direction_lookup(hourly['windDirection'].get(provider, no_data_value)),
                    'wind_gust_mph': float(hourly['gust'].get(provider, no_data_value)),
                    'relative_humidity_percentage': float(hourly['humidity'].get(provider, no_data_value)),
                    'visibility': open_weather_visibility_lookup(hourly['visibility'].get(provider, no_data_value)),
                    'uv_index': None,
                    'weather_type': None,
                    'precipitation_probability_percentage': None,
                }
                processed_weather_data[provider].append(processed_data)
        return processed_weather_data


# storm_glass = StormGlassClient()
# print('the_rainery get_forecast_lat_lon', storm_glass.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('storm_glass get_forecast_postcode',
#       storm_glass.get_forecast_postcode('GB', 'b17 0hs'))
# print('storm_glass get_forecast_city_country',
#       storm_glass.get_forecast_city_country("Birmingham", "uk"))
