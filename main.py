from dotenv import load_dotenv
import os
import requests
from abc import ABC, abstractmethod
from math import radians, cos, sin, asin, sqrt
from xml.etree import ElementTree
import pgeocode
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from typing import Tuple

from definitions import *


# Load env variables
load_dotenv()
MET_OFFICE_API_KEY = os.getenv("MET_OFFICE_API_KEY")
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
ACCUWEATHER_API_KEY = os.getenv("ACCUWEATHER_API_KEY")
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")
THE_RAINERY_API_KEY = os.getenv("THE_RAINERY_API_KEY")
STORM_GLASS_API_KEY = os.getenv("STORM_GLASS_API_KEY")
WEATHERBIT_IO_API_KEY = os.getenv("WEATHERBIT_IO_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


class WeatherDataClient(ABC):
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def process_data(self, data: any):
        raise NotImplementedError

    @abstractmethod
    def get_forecast_lat_lon(self, lat: float, lon: float):
        raise NotImplementedError

    def get_forecast_postcode(self, country: str, postcode: str):
        lat, lon = self.geocode_postcode(country, postcode)
        return self.get_forecast_lat_lon(lat, lon)

    def get_forecast_city_country(self, city, country):
        lat, lon = self.geocode_city_country(city, country)
        return self.get_forecast_lat_lon(
            lat=lat, lon=lon)

    @staticmethod
    def geocode_postcode(country_code: str, postcode: str) -> Tuple[float, float]:
        """Returns the lat and lon of the nearest point to the provided postcode"""
        if country_code not in pgeocode.COUNTRIES_VALID:
            raise ValueError("Country code must be one of: " +
                             ', '.join(pgeocode.COUNTRIES_VALID))
        nomi = pgeocode.Nominatim(country_code)
        query = nomi.query_postal_code(postcode)
        if str(query['latitude']) == 'nan' or str(query['longitude']) == 'nan':
            raise ValueError("Couldn't geocode that postcode.")
        return query['latitude'], query['longitude']

    @staticmethod
    def geocode_city_country(city: str, country: str) -> Tuple[float, float]:
        """Returns the lat / lon of the city / country combination"""
        geolocator = Nominatim(user_agent="my_test")
        location = geolocator.geocode(f"{city}, {country}")
        return location.latitude, location.longitude

    @staticmethod
    def haversine(lat1: str, lon1: str, lat2: str, lon2: str) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        lat1, lon1, lat2, lon2 = float(lat1), float(
            lon1), float(lat2), float(lon2)
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        return c * r


# Met office
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

    def get_forecast(self, location_code=None):
        if not location_code:
            location_code = self.location_code
        data = requests.get(
            f"{self.base_url}val/wxfcs/all/json/{location_code}?res=3hourly&key={MET_OFFICE_API_KEY}")
        return data.json()

    def get_forecast_lat_lon(self, lat: float, lon: float):
        """
        Return 3 days of forecast data based on the provided lat and lon
        """
        closest_location_id = self.get_closest_location(lat, lon)['id']
        forecast = self.get_forecast(location_code=closest_location_id)
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


# BBC Weather RSS
class BBCClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/2643123"
        temp = "weather-broker-cdn.api.bbci.co.uk/en/maps/forecasts-observations/03131311"
        # 03131123
        # 03131301
        # 03131132
        # 03131310
        # 03131133
        # 03131311
        temp = "weather-broker-cdn.api.bbci.co.uk/en/forecast/aggregated/2655603"

    def get_forecast(self):
        response = requests.get(self.base_url)
        tree = ElementTree.fromstring(response.content)
        print(tree.find("channel/title").text)
        print(tree.find("channel/item/description").text)
        print(tree.findall("channel/item/description"))
        # print(tree.find("channel/title").text)


# bbc = BBCClient()
# bbc.get_forecast()


# Open Weather
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


open_weather = OpenWeatherClient()
# print('get_forecast_lat_lon', open_weather.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('get_forecast_postcode',
#       open_weather.get_forecast_postcode('GB', 'b17 0hs'))
# print('get_forecast_city_country',
#       open_weather.get_forecast_city_country("Birmingham", "uk"))


# AccuWeather
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

    def get_forecast(self, location_code):
        endpoint = f"/forecasts/v1/hourly/12hour/{location_code}"
        response = requests.get(self.base_url + endpoint, params=self.params)
        return response.json()

    def get_forecast_lat_lon(self, lat, lon):
        location_code = self.get_location_code(lat, lon)
        forecast_data = self.get_forecast(location_code=location_code)
        return forecast_data

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
        return forecast_data

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


class TheRaineryClient(WeatherDataClient):
    def __init__(self):
        self.headers = {'x-api-key': THE_RAINERY_API_KEY}
        self.base_url = 'https://api.therainery.com/forecast/weather'

    def get_forecast_lat_lon(self, lat, lon):
        response = requests.get(self.base_url, params={'latitude': lat,
                                                       'longitude': lon}, headers=self.headers)
        raw_data = response.json()
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


class WeatherApiClient(WeatherDataClient):
    def __init__(self):
        self.base_url = f"http://api.weatherapi.com/v1/"

    def get_forecast_lat_lon(self, lat, lon):
        endpoint = "forecast.json"
        response = requests.get(self.base_url + endpoint, params={'key': WEATHER_API_KEY,
                                                                  'q': f"{lat},{lon}", 'days': 5, 'aqi': 'no', 'alerts': 'no'})
        print(response.json())

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


weather_api = WeatherApiClient()
# print('the_rainery get_forecast_lat_lon', weather_api.get_forecast_lat_lon(
#     lat=50.73862, lon=-2.90325))
# print('weather_api get_forecast_postcode',
#       weather_api.get_forecast_postcode('GB', 'b17 0hs'))
# print('weather_api get_forecast_city_country',
#       weather_api.get_forecast_city_country("Birmingham", "uk"))
