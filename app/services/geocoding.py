import time
from typing import Any

from geopy.geocoders import Nominatim
from geopy.adapters import GeocoderTimedOut


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
        return 'no data'
    return inner


@backoff
def get_location(geolocator, coordinates: tuple[float, float]) -> str:
    location = geolocator.reverse(coordinates, exactly_one=True)
    return location.address


def reverse_geocode(points: list) -> list[dict[str, Any]]:
    geolocator = Nominatim(user_agent="geocode-revers")
    addresses = []

    for point in points:
        coordinates = (point[1], point[2])
        address = get_location(geolocator, coordinates)
        addresses.append({'name': point[0], 'address': address, 'lat': point[1], 'lon': point[2]})

    return addresses
