from typing import *
import numpy as np
import rasterio
import rasterio.features
from pyproj import CRS
from rasterio.enums import Resampling
from shapely.geometry import box


def get_bands_as_arrays(bands, crop):
    bands.sort(key=lambda band: band.spatial_resolution)
    resample = None
    affine_transform = None
    band_arrays = {}
    for band in bands:
        band_array, affine_transform = get_band_as_array(band.path, crop, resample)
        if not resample: resample = band_array.shape
        band_arrays[band.name] = band_array
    return band_arrays, affine_transform


def mask_clouds_and_snow(array, cloud_mask_array, snow_mask_array):
    return np.ma.array(array,
                       mask=((cloud_mask_array > 0) | (snow_mask_array > 0) | array.mask),
                       dtype=np.float32,
                       fill_value=-999)


def get_band_as_array(
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
        band_masked = np.ma.array(data[0], mask=geometry_mask, dtype=np.float32, fill_value=-999)

        return band_masked, geometry_transform
