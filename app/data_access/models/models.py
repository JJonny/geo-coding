from collections import namedtuple


Point = namedtuple('Point', ['name', 'lat', 'lon'])
PointAddress = namedtuple('PointAddress', ['name', 'address', 'lat', 'lon'])
Distance = namedtuple('Distance', ['name', 'distance'])