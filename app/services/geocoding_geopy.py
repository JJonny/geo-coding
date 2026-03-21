import logging
import time
from functools import wraps
from typing import Optional

from geopy.adapters import GeocoderTimedOut
from geopy.geocoders import Nominatim

from app.data_access.models.models import PointAddress, Point
from app.services.geocoding import Geocoding

logger = logging.getLogger(__name__)

NOMINATIM_RATE_LIMIT_SECONDS = 1.0


def backoff(
    start_sleep_time: float = 3.0, factor: int = 2, border_sleep_time: int = 30
):
    """
    t = start_sleep_time * 2^(n) if t < border_sleep_time
    t = border_sleep_time if t >= border_sleep_time

    :param start_sleep_time: initial retry time
    :param factor: by how much to increase the wait time
    :param border_sleep_time: maximum wait time
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_time_sleep = start_sleep_time
            try_count = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except GeocoderTimedOut:
                    time.sleep(current_time_sleep)

                    if current_time_sleep < border_sleep_time:
                        current_time_sleep = start_sleep_time * factor**try_count
                    else:
                        break
                    try_count += 1
                    logger.info("Timeout service occurred. Coordinates: %s", args[1])
            logger.warning(
                "The service can't provide data for the coordinates: %s", args[1]
            )
            return None

        return inner

    return wrapper


class GeoCodingGeopy(Geocoding):
    """Reverse geocoding service using geopy/Nominatim."""

    def __init__(self):
        self.geolocator = Nominatim(user_agent="geocode-reverse")

    @backoff()
    def _get_location(self, coordinates: tuple[float, float]) -> Optional[str]:
        """Get readable address by coordinates."""
        location = self.geolocator.reverse(coordinates, exactly_one=True)
        if location is None:
            return None
        return location.address

    def reverse_geocode(self, coordinates_list: list[Point]) -> list[PointAddress]:
        """Collect all addresses by coordinates."""
        addresses: list[PointAddress] = []

        for point in coordinates_list:
            coordinates = (point.lat, point.lon)
            address = self._get_location(coordinates)
            addresses.append(PointAddress(point.name, address or "no data", point.lat, point.lon))
            time.sleep(NOMINATIM_RATE_LIMIT_SECONDS)

        return addresses
