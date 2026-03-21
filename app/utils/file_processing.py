import csv
import io
import logging

from app.data_access.models.models import Point, PointAddress
from app.services.geocoding_geopy import GeoCodingGeopy

logger = logging.getLogger(__name__)

MAX_POINTS = 10_000


def process_geo_data(points: list[Point]) -> dict[str, list[PointAddress]]:
    """
    Receive points, reverse-geocode them to get readable addresses.
    Distance calculation is performed in the DB layer via PostGIS.
    """
    addresses: list[PointAddress] = GeoCodingGeopy().reverse_geocode(points)
    return {"points": addresses}


def process_file_data(file_data: io.TextIOBase) -> list[Point]:
    """Read csv file. Transform data to list of Point values. Skips invalid rows."""
    points: list[Point] = []

    csv_reader = csv.reader(file_data)
    next(csv_reader, None)  # skip header

    def is_valid(lat: float, lon: float) -> bool:
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)

    for row_number, row in enumerate(csv_reader, start=2):
        if len(points) >= MAX_POINTS:
            logger.warning("Reached maximum allowed points limit (%d). Remaining rows skipped.", MAX_POINTS)
            break

        if len(row) < 3:
            logger.warning("Row %d skipped. Wrong count of elements in the row.", row_number)
            continue

        try:
            point_name = row[0]
            lat = float(row[1])
            lon = float(row[2])
        except ValueError as e:
            logger.error("Conversion error in row %d: %s", row_number, e)
            continue

        if not is_valid(lat, lon):
            logger.error("Incorrect latitude/longitude data in row %d.", row_number)
            continue

        points.append(Point(point_name, lat, lon))

    return points
