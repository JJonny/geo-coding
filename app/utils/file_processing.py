import csv
import logging

from app.data_access.models.models import Distance, Point, PointAddress
from app.services.calculation_dist import calculate_all_distances
from app.services.geocoding_geopy import GeoCodingGeopy


logger = logging.getLogger(__name__)


def process_geo_data(points: list[Point]) -> dict[str, [Distance | PointAddress]]:
    """
    Receive points and calculate all distinct links between each point including distance in meters.
    And generate readable addresses
    """
    distance: list[Distance] = calculate_all_distances(points)
    addresses: list[PointAddress] = GeoCodingGeopy().reverse_geocode(points)

    result_data = {
        "points": addresses,
        "links": distance,
    }
    return result_data


def process_file_data(file_data) -> list[Point]:
    """Read csv file. Transform data to list of values"""
    points: list[Point] = []

    csv_reader = csv.reader(file_data)
    # Skip headers
    next(csv_reader, None)

    def is_valid(lat: float, lon: float) -> bool:
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)

    for row_number, row in enumerate(csv_reader, start=2):
        if len(row) < 3:
            logger.warning(f"Row {row_number} skipped. Wrong count of elements in the row.")
            continue

        try:
            point_name = row[0]
            lat = float(row[1])
            lon = float(row[2])
        except ValueError as e:
            logger.error(f"Conversion error in the row {row_number}: {str(e)}")
            continue

        if not is_valid(lat, lon):
            logger.error(f"Incorrect latitude/longitude data in the row {row_number}.")
            continue

        points.append(Point(point_name, lat, lon))

    return points
