import csv
import random
import uuid


def generate_csv(num_points: int = 5_000):
    """Generate unique coordinates within a specific range"""
    def generate_coordinates():
        latitude = round(random.uniform(49.0, 51.0), 6)  # Range for latitude
        longitude = round(random.uniform(29.0, 35.0), 6)  # Range for longitude
        return latitude, longitude


    data = []
    for _ in range(num_points):
        latitude, longitude = generate_coordinates()
        data.append((str(uuid.uuid4()), latitude, longitude))

    csv_filename = "points.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Point", "Latitude", "Longitude"])
        writer.writerows(data)


if __name__ == '__main__':
    generate_csv()