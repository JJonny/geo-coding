from abc import ABC, abstractmethod
from typing import Any

from app.data_access.models.models import Point, PointAddress


class Geocoding(ABC):
    """Interface for reverse geocoding service."""

    @abstractmethod
    def reverse_geocode(self, coordinates_list: list[Point]) -> list[PointAddress]:
        pass
