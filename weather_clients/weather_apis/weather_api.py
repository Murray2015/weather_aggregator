from datetime import datetime
import requests
from os import getenv

from .base import WeatherDataClient
from .utils.definitions import open_weather_visibility_lookup, uv_lookup_codes

# weatherapi.com
WEATHER_API_KEY = getenv("WEATHER_API_KEY")


class WeatherApiClient(WeatherDataClient):
    def __init__(self):
        self.base_url = f"http://api.weatherapi.com/v1/"

    def get_forecast_lat_lon(self, lat, lon):
        endpoint = "forecast.json"
        response = requests.get(self.base_url + endpoint, params={'key': WEATHER_API_KEY,
                                                                  'q': f"{lat},{lon}", 'days': 5, 'aqi': 'no', 'alerts': 'no'})
        # print(response.json())
        return response.json()

    def process_data(self, data: any):
        processed_weather_data = []
        lat = data['location']['lat']
        lon = data['location']['lon']
        place_name = data['location']['name'] + \
            data['location']['region'] + data['location']['country']
        for day in data['forecast']['forecastday']:
            for hourly in day['hour']:
                processed_data = {
                    'lat': lat,
                    'lon': lon,
                    'place_name': place_name,
                    'date_time': datetime.fromtimestamp(hourly['time_epoch']),
                    'temperature_celcius': float(hourly['temp_c']),
                    'feels_like_temperature_celcius': float(hourly['feelslike_c']),
                    'wind_speed_kph': float(hourly['wind_kph']),
                    'wind_direction': hourly['wind_dir'],
                    'wind_gust_kph': float(hourly['gust_kph']),
                    'relative_humidity_percentage': float(hourly['humidity']),
                    'visibility': open_weather_visibility_lookup(hourly['vis_km'] * 1000),
                    'uv_index': {'code': hourly['uv'], 'description': uv_lookup_codes[str(int(hourly['uv']))]},
                    'weather_type': hourly['condition']['text'],
                    'precipitation_probability_percentage': hourly['chance_of_rain'],
                }
                processed_weather_data.append(processed_data)
        return processed_weather_data


# weather_api = WeatherApiClient()
# print('the_rainery get_forecast_lat_lon', weather_api.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('weather_api get_forecast_postcode',
#       weather_api.get_forecast_postcode('GB', 'b17 0hs'))
# print('weather_api get_forecast_city_country',
#       weather_api.get_forecast_city_country("Birmingham", "uk"))
