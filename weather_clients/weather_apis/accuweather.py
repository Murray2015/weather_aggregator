import requests
import json
from datetime import datetime
from os import getenv
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat

from .base import WeatherDataClient
from .utils.definitions import accuweather_weather_code_lookup, no_data_value, open_weather_visibility_lookup, uv_lookup_codes

# AccuWeather
ACCUWEATHER_API_KEY = getenv("ACCUWEATHER_API_KEY")


class AccuWeatherClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "http://dataservice.accuweather.com/"
        self.params = {
            'apikey': ACCUWEATHER_API_KEY,
            'language': 'en-us',
            'details': "true",
            'metric': 'true'
        }

    def get_location_code(self, lat, lon):
        endpoint = "locations/v1/cities/geoposition/search"
        lat_lon = {'q': f'{lat},{lon}'}
        response = requests.get(self.base_url + endpoint,
                                params={**self.params, **lat_lon})
        response_data = response.json()
        return response_data['Key']

    async def get_forecast(self, location_code):
        http_client = AsyncHTTPClient()
        try:
            endpoint = url_concat(
                self.base_url + f"/forecasts/v1/hourly/12hour/{location_code}", self.params)
            response = await http_client.fetch(endpoint)
        except Exception as e:
            print("Error: %s" % e)
        return json.loads(response.body)

    async def get_forecast_lat_lon(self, lat, lon):
        location_code = self.get_location_code(lat, lon)
        forecast_data = await self.get_forecast(location_code=location_code)
        processed_data = self.process_data(forecast_data, lat, lon)
        return processed_data

    def process_data(self, data, lat, lon):
        processed_weather_data = []
        place_name = None
        for hourly in data:
            processed_data = {
                'lat': lat,
                'lon': lon,
                'place_name': place_name,
                'date_time': datetime.fromtimestamp(hourly['EpochDateTime']),
                'temperature_celcius': float(hourly['Temperature']['Value']),
                'feels_like_temperature_celcius': float(hourly['RealFeelTemperature']['Value']),
                'wind_speed_kph': float(hourly['Wind']['Speed']['Value']),
                'wind_direction': hourly['Wind']['Direction']['Localized'],
                'wind_gust_mph': float(hourly['WindGust']['Speed']['Value']),
                'relative_humidity_percentage': float(hourly['RelativeHumidity']),
                'visibility': open_weather_visibility_lookup(hourly['Visibility']['Value'] * 1000),
                'uv_index': {'code': hourly['UVIndex'], 'description': uv_lookup_codes[str(hourly['UVIndex'])]},
                'weather_type': accuweather_weather_code_lookup[hourly['WeatherIcon']],
                'precipitation_probability_percentage': float(hourly['PrecipitationProbability']),
            }
            processed_weather_data.append(processed_data)
        return processed_weather_data

    def get_forecast_postcode(self, country, postcode):
        lat, lon = self.geocode_postcode(country, postcode)
        location_code = self.get_location_code(lat, lon)
        forecast_data = self.get_forecast(location_code=location_code)
        processed_data = self.process_data(forecast_data, lat, lon)
        return processed_data

    def get_forecast_city_country(self, city, country):
        lat, lon = self.geocode_city_country(city, country)
        location_code = self.get_location_code(lat, lon)
        forecast_data = self.get_forecast(location_code=location_code)
        processed_data = self.process_data(forecast_data, lat, lon)
        return processed_data


# accuweather = AccuWeatherClient()
# print('accuweather get_forecast_lat_lon', accuweather.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('accuweather get_forecast_postcode',
#       accuweather.get_forecast_postcode('GB', 'b17 0hs'))
# print('accuweather get_forecast_city_country',
#       accuweather.get_forecast_city_country("Birmingham", "uk"))
