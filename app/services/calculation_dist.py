from geopy.distance import great_circle     # faster then geodesic

from app.data_access.models.models import Distance, Point


def get_distance(point1: Point, point2: Point) -> Distance:
    """Calculate distance between two points."""
    name = f"{point1.name}{point2.name}"
    coords_1 = (point1.lat, point1.lon)
    coords_2 = (point2.lat, point2.lon)
    distance = great_circle(coords_1, coords_2).meters
    return Distance(name, distance)


def calculate_all_distances(points: list[Point]) -> list[Distance]:
    """Calculate all distances from list of points."""
    distances: list[Distance] = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = get_distance(points[i], points[j])
            distances.append(dist)

    return distances
