from geopy.distance import great_circle     # faster then geodesic


def get_distance(point1: list, point2: list) -> dict[str, float]:
    """Calculate distance between to points."""
    name = f"{point1[0]}{point2[0]}"
    coords_1 = (point1[1], point1[2])
    coords_2 = (point2[1], point2[2])
    distance = great_circle(coords_1, coords_2).meters
    return {"name": name, "distance": distance}


def calculate_all_distances(points: dict[str, tuple[float, float]]) -> list[dict]:
    """Calculate all distances from list of points."""
    distances = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = get_distance(points[i], points[j])
            distances.append(dist)

    return distances
