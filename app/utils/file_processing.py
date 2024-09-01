import csv

from app.services.calculation_dist import calculate_all_distances
from app.services.geocoding import reverse_geocode


def process_geo_data(points):
    """
    Receive points and calculate all distinct links between each point including distance in meters.
    And generate readable addresses
    """
    distance = calculate_all_distances(points)
    addresses = reverse_geocode(points)

    result_data = {
        "points": addresses,
        "links": distance,
    }
    return result_data


def process_file_data(file_data) -> list[list]:
    """Read csv file. Transform data to list of values"""
    points = []

    csv_reader = csv.reader(file_data)

    # Skip header line
    next(csv_reader)
    for row in csv_reader:
        points.append([row[0], float(row[1]), float(row[2])])

    return points
