from abc import ABC, abstractmethod
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt
import pgeocode
from typing import Tuple


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
