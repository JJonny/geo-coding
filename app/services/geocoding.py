from abc import ABC, abstractmethod
from typing import Any


class Geocoding(ABC):
    """Interface for reverse geo coding service."""

    @abstractmethod
    def _get_location(self, coordinates: tuple[float, float], **kwargs):
        pass

    @abstractmethod
    def reverse_geocode(self, coordinates_list: list[Any]):
        pass
