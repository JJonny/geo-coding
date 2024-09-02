import logging
import time
from typing import Any

from geopy.geocoders import Nominatim
from geopy.adapters import GeocoderTimedOut

from app.services.geocoding import Geocoding


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backoff(func):
    def inner(*args, **kwargs):
        threshold = 0
        while threshold < 3:
            try:
                ret_value = func(*args, **kwargs)
                return ret_value
            except GeocoderTimedOut:
                threshold += 1
                time.sleep(30)
                logger.info(f"Timeout service occurred. Coordinates: {kwargs.get('coordinates')}")
        logger.warning(f"The service can't provide data for the coordinates: {kwargs.get('coordinates')}")
        return 'no data'
    return inner


class GeoCodingGeopy(Geocoding):

    def __init__(self):
        self.geolocator = Nominatim(user_agent="geocode-revers")

    @backoff
    def _get_location(self, coordinates: tuple[float, float]) -> str:
        location = self.geolocator.reverse(coordinates, exactly_one=True)
        return location.address

    def reverse_geocode(self, points: list) -> list[dict[str, Any]]:
        addresses = []

        for point in points:
            coordinates = (point[1], point[2])
            address = self._get_location(coordinates)
            addresses.append({'name': point[0], 'address': address, 'lat': point[1], 'lon': point[2]})

        return addresses
