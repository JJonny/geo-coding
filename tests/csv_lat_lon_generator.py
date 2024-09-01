import csv
import random

def generate_csv(num_points: int = 5000):
    """Generate unique coordinates within a specific range"""
    def generate_coordinates():
        latitude = random.uniform(49.0, 51.0)  # Range for latitude
        longitude = random.uniform(29.0, 35.0)  # Range for longitude
        return latitude, longitude

    # Generate the list of point names: A-Z, then AA, AB, etc.
    points = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for first in [""] + list(letters):
        for second in letters:
            points.append(f"{first}{second}")
            if len(points) >= num_points:
                break
        if len(points) >= num_points:
            break

    data = []
    for point in points:
        latitude, longitude = generate_coordinates()
        data.append((point, latitude, longitude))

    csv_filename = "points.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Point", "Latitude", "Longitude"])
        writer.writerows(data)


if __name__ == '__main__':
    generate_csv()