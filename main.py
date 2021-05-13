from dotenv import load_dotenv
import os
import requests
from abc import ABC
from math import radians, cos, sin, asin, sqrt
from xml.etree import ElementTree
import pgeocode


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


class WeatherDataClient():
    def __init__(self):
        raise NotImplementedError

    def get_forecast(self):
        raise NotImplementedError

    @staticmethod
    def geocode_postcode(country, postcode):
        """Returns the lat and lon of the nearest point to the provided postcode"""
        nomi = pgeocode.Nominatim(country)
        query = nomi.query_postal_code(postcode)
        return (query['latitude'], query['longitude'])

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
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
        self.location_code = 355998

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

    def get_forecast(self, location_code=None):
        if not location_code:
            location_code = self.location_code
        data = requests.get(
            f"{self.base_url}val/wxfcs/all/json/{location_code}?res=3hourly&key={MET_OFFICE_API_KEY}")
        return data.json()


# Met office testing
# met_office_client = MetOfficeClient()
# # print("data", met_office_client.get_forecast())
# print("code", met_office_client.get_location_code("Lizard Lighthouse"))
# print("code", met_office_client.get_location_code(lat=50.73862, lon=-2.90325))


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
    def __init__(self):
        lat = 52.4862
        lon = -1.8904
        part = "minutely"
        self.url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={OPEN_WEATHER_API_KEY}"

    def get_forecast(self):
        return requests.get(self.url).content


# open_weather = OpenWeatherClient()
# print(open_weather.geocode_postcode('gb', 'tq12 5sa'))
# print(open_weather.get_forecast())


# AccuWeather
class AccuWeatherClient(WeatherDataClient):
    def __init__(self):
        self.url = "http://dataservice.accuweather.com/forecasts/v1/hourly/120hour/{locationKey}"
        self.location_url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"

    def get_location_code(self, lat, lon):
        endpoint = f"?apikey={ACCUWEATHER_API_KEY}&q={lat}%2C{lon}&language=en-us&details=true"
        response = requests.get(self.location_url + endpoint)
        response_data = response.json()
        print(response_data)
        self.location_code = response_data['Key']

    def get_forecast(self):
        endpoint = f"/forecasts/v1/hourly/12hour/{self.location_code}?apikey={ACCUWEATHER_API_KEY}&language=en-gb&details=true&metric=true"
        response = requests.get(self.url)
        print(response.text)


accuweather = AccuWeatherClient()
accuweather.get_location_code(lat=52.5, lon=-2)
accuweather.get_forecast()


class TomorrowIOClient(WeatherDataClient):
    def __init__(self):
        self.url = f'https://api.tomorrow.io/v4/timelines?location=-73.98529171943665,40.75872069597532&fields=temperature,precipitationIntensity,precipitationType,windSpeed,windGust,windDirection,temperature,temperatureApparent,cloudCover,cloudBase,cloudCeiling,weatherCode&timesteps=1h&units=metric&apikey={TOMORROW_API_KEY}'

    def get_forecast(self):
        res = requests.get(self.url)
        print(res.content)


# tomorrow_io = TomorrowIOClient()
# tomorrow_io.get_forecast()


class TheRaineryClient(WeatherDataClient):
    def __init__(self):
        self.headers = {'x-api-key': THE_RAINERY_API_KEY}

    def get_forecast(self):
        response = requests.get('https://api.therainery.com/forecast/weather',
                                params={
                                    'latitude': 48.8582,
                                    'longitude': 2.2945,
                                }, headers=self.headers)

        print(response.text)


# the_rainery = TheRaineryClient()
# the_rainery.get_forecast()

class StormGlassClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "https://api.stormglass.io/v2"
        self.weather_endpoint = "/weather/point"
        self.params = {"lat": 52, "lng": -1, "params": ','.join(['airTemperature', 'pressure', 'cloudCover', 'gust', 'humidity', 'precipitation', 'swellDirection', 'swellHeight', 'swellPeriod',
                                                                'secondarySwellPeriod', 'secondarySwellDirection', 'secondarySwellHeight', 'visibility', 'waterTemperature', 'waveDirection', 'waveHeight', 'wavePeriod', 'windDirection', 'windSpeed'])}
        self.headers = {'Authorization': STORM_GLASS_API_KEY
                        }

    def get_forecast(self):
        response = requests.get(
            self.base_url + self.weather_endpoint, params=self.params, headers=self.headers)
        print(response.json())


# storm_glass = StormGlassClient()
# storm_glass.get_forecast()

class WeatherbitIoClient(WeatherDataClient):
    def __init__(self):
        self.base_url = "http://api.weatherbit.io/v2.0/forecast/hourly"
        self.endpoint = F"?lang=en&key={WEATHERBIT_IO_API_KEY}"

    def get_forecast(self, city=None, country=None, lat=None, lon=None):
        if city and country:
            response = requests.get(
                self.base_url + self.endpoint + f"&city={city}&country={country}")
        elif lat and lon:
            response = requests.get(
                self.base_url + self.endpoint + f"&lat={lat}&lon={lon}")
        print(response.json())


# weatherbit_io = WeatherbitIoClient()
# weatherbit_io.get_forecast(city="Birmingham", country="UK")


class WeatherApiClient(WeatherDataClient):
    def __init__(self):
        self.base_url = f"http://api.weatherapi.com/v1/"

    def get_forecast(self, city=None, postcode=None):
        endpoint = f"forecast.json?key={WEATHER_API_KEY}&q={city or postcode}&days=3&aqi=no&alerts=no"
        response = requests.get(self.base_url + endpoint)
        print(response.json())


weather_api = WeatherApiClient()
weather_api.get_forecast("Birmingham")
