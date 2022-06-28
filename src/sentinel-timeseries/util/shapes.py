import json

from shapely.geometry import shape


def get_polygon_from_geojson(file_path: str):
    """ Returns a single shapely Polygon from a geojson file. """
    with open(file_path, 'r') as f:
        features = json.load(f)['features']
        polygon = shape(features[0]["geometry"])
    return polygon
