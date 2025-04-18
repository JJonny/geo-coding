import logging
import time
from functools import wraps
from typing import Any

from geopy.adapters import GeocoderTimedOut
from geopy.geocoders import Nominatim

from app.services.geocoding import Geocoding

logger = logging.getLogger(__name__)


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
                except Exception as e:
                    time.sleep(current_time_sleep)

                    if current_time_sleep < border_sleep_time:
                        current_time_sleep = start_sleep_time * factor**try_count
                    else:
                        break
                    try_count += 1
                    logger.info(f"Timeout service occurred. Coordinates: {args[1]}")
            logger.warning(
                f"The service can't provide data for the coordinates: {args[1]}"
            )
            return "no data"

        return inner

    return wrapper


class GeoCodingGeopy(Geocoding):
    """Revers Geo coding service. Used geopy lib."""

    def __init__(self):
        self.geolocator = Nominatim(user_agent="geocode-revers")

    @backoff()
    def _get_location(self, coordinates: tuple[float, float]) -> str:
        """Get readable address by coordinates."""

        location = self.geolocator.reverse(coordinates, exactly_one=True)
        return location.address

    def reverse_geocode(self, points: list) -> list[dict[str, Any]]:
        """Collect all addresses by coordinates."""
        addresses = []

        for point in points:
            coordinates = (point[1], point[2])
            address = self._get_location(coordinates)
            addresses.append(
                {"name": point[0], "address": address, "lat": point[1], "lon": point[2]}
            )

        return addresses
