import requests
import json
from datetime import datetime, timedelta
from os import getenv
from tornado.httpclient import AsyncHTTPClient

from .base import WeatherDataClient
from .utils.definitions import visibility_lookup_codes, uv_lookup_codes, weather_lookup_codes


# Met office
MET_OFFICE_API_KEY = getenv("MET_OFFICE_API_KEY")


class MetOfficeClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "http://datapoint.metoffice.gov.uk/public/data/"
        self.locations = self.load_locations()
        self.location_code = None

    def load_locations(self):
        locations_response = requests.get(
            f"{self.base_url}val/wxfcs/all/json/sitelist?key={MET_OFFICE_API_KEY}")
        data = locations_response.json()
        locations = data['Locations']['Location']
        return locations

    def get_location_code(self, place_name=None, lat=None, lon=None):
        if place_name:
            try:
                loc = list(filter(lambda x: x['name']
                                  == place_name, self.locations))

                self.location_code = loc[0]['id']
            except Exception as e:
                print("Place name not found", e)
        elif lat and lon:
            self.location_code = self.get_closest_location(lat, lon)['id']
        return self.location_code

    def get_closest_location(self, lat, lon):
        # Get distances
        locations = self.locations.copy()
        for location in locations:
            location['dist'] = self.haversine(
                lat, lon, location['latitude'], location['longitude'])
        # Sort on distances and return closest
        return sorted(locations, key=lambda x: x['dist'])[0]

    def process_data(self, data):
        '''Takes raw met office data and processes into a list of dicts'''

        processed_weather_data = []
        lat = float(data['SiteRep']['DV']['Location']['lat'])
        lon = float(data['SiteRep']['DV']['Location']['lon'])
        place_name = data['SiteRep']['DV']['Location']['name']
        for day in data['SiteRep']['DV']['Location']['Period']:
            for three_hourly in day['Rep']:
                processed_data = {
                    'lat': lat,
                    'lon': lon,
                    'place_name': place_name,
                    'date_time': datetime.strptime(day['value'], '%Y-%M-%dZ') + timedelta(minutes=int(three_hourly['$'])),
                    'temperature_celcius': float(three_hourly['T']),
                    'feels_like_temperature_celcius': float(three_hourly['F']),
                    'wind_gust_mph': float(three_hourly['G']),
                    'relative_humidity_percentage': float(three_hourly['H']),
                    'visibility': visibility_lookup_codes[three_hourly['V']],
                    'wind_direction': three_hourly['D'],
                    'wind_speed_mph': float(three_hourly['S']),
                    'uv_index': {'code': three_hourly['U'], 'description': uv_lookup_codes[str(three_hourly['U'])]},
                    'weather_type': weather_lookup_codes[three_hourly['W']],
                    'precipitation_probability_percentage': float(three_hourly['Pp']),
                }
                processed_weather_data.append(processed_data)
        return processed_weather_data

    async def get_forecast(self, location_code=None):
        if not location_code:
            location_code = self.location_code
        try:
            http_client = AsyncHTTPClient()
            response = await http_client.fetch(f"{self.base_url}val/wxfcs/all/json/{location_code}?res=3hourly&key={MET_OFFICE_API_KEY}")
        except Exception as e:
            print("Error: %s" % e)
        return json.loads(response.body)

    async def get_forecast_lat_lon(self, lat: float, lon: float):
        """
        Return 3 days of forecast data based on the provided lat and lon
        """
        closest_location_id = self.get_closest_location(lat, lon)['id']
        forecast = await self.get_forecast(location_code=closest_location_id)
        processed_data = self.process_data(forecast)
        return processed_data


# Met office testing
# met_office_client = MetOfficeClient()
# print('Met office get_forecast_lat_lon', met_office_client.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('Met office get_forecast_postcode',
#       met_office_client.get_forecast_postcode('GB', 'b17 0hs'))
# print('Met office get_forecast_city_country',
#       met_office_client.get_forecast_city_country("Birmingham", "uk"))
