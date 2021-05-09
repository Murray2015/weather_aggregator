from dotenv import load_dotenv
import os
import requests
from abc import ABC
from math import radians, cos, sin, asin, sqrt
from xml.etree import ElementTree


# Load env variables
load_dotenv()
MET_OFFICE_API_KEY = os.getenv("MET_OFFICE_API_KEY")


class WeatherDataClient():
    def __init__(self):
        raise NotImplementedError

    def get_forecast(self):
        raise NotImplementedError

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

    def get_forecast(self):
        response = requests.get(self.base_url)
        tree = ElementTree.fromstring(response.content)
        print(tree.find("channel/title").text)
        print(tree.find("channel/item/description").text)
        print(tree.findall("channel/item/description"))
        # print(tree.find("channel/title").text)


bbc = BBCClient()
bbc.get_forecast()
