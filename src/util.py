import json
import numpy as np
import rasterio
import rasterio.features
from pyproj import CRS
from rasterio.enums import Resampling
from shapely.geometry import shape, box


def calculate_normalized_index(band1, band2):
    """ Returns a normalized index from two bands. """
    return (band1 - band2) / (band1 + band2)


def get_polygon_from_geojson(file_path: str):
    """ Returns a single shapely Polygon from a geojson file. """
    with open(file_path, 'r') as f:
        features = json.load(f)['features']
        polygon = shape(features[0]["geometry"])
    return polygon


def get_image_data(
        image_path: str,
        crop_shape,
        resample=None
):
    """
  image_path: Opens a image using rasterIO given an image path.
  zone: Clips the image to the zone, this should be some kind of Polygon.
  resample: Resamples the image to given dimensions.
  """
    with rasterio.open(image_path) as ds:
        assert ds.crs == CRS.from_epsg(4326)  # Raise error if image does not have the right CRS
        bounding_box = box(*crop_shape.bounds)

        # Crop raster -- get bounding window of shape(s) in raster.
        window = rasterio.features.geometry_window(ds, [bounding_box])
        window_transform = ds.window_transform(window)

        # Either set a new shape for the data or use the window's shape.
        out_shape = (resample[0], resample[1]) if isinstance(resample, tuple) else (window.height, window.width)

        # Limit raster to window, apply resampling if desired.
        data = ds.read(
            out_shape=out_shape,
            window=window,
            resampling=Resampling.cubic
        )
        # We have to transform the window (our cropped view) to a resampled view if we resampled.
        geometry_transform = window_transform * window_transform.scale((window.width / data.shape[-1]),
                                                                       (window.height / data.shape[-2]))
        # Apply geometry mask.
        geometry_mask = rasterio.features.geometry_mask([crop_shape], data[0].shape, geometry_transform)
        band_masked = np.ma.array(data[0], mask=geometry_mask, dtype=np.int16, fill_value=0)

        return band_masked, geometry_transform
