from typing import NamedTuple, Optional


class Point(NamedTuple):
    name: str
    lat: float
    lon: float


class PointAddress(NamedTuple):
    name: str
    address: str
    lat: float
    lon: float


class Distance(NamedTuple):
    name: str
    distance: float
