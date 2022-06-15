# A code that calculates the Indices based on downloaded Sentinel 2 data
import json
from functools import partial

import numpy as np
import pyproj
import rasterio
import rasterio.features
import shapely
from rasterio.enums import Resampling
from rasterio.plot import show
from shapely.geometry import shape, box
from shapely.ops import transform


def calculate_normalized_index(band1, band2):
    """ Returns a normalized index from two bands. """
    return (band1 - band2) / (band1 + band2)


def get_study_area(file_path):
    """ Returns the study area as shapely Polygon. """
    with open(file_path, 'r') as f:
        aoi_json = json.load(f)['features']
        aoi_shape = shape(aoi_json[0]["geometry"])
    return aoi_shape


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
        tfm = partial(pyproj.transform,
                      pyproj.Proj(28992),  # Assuming the study / crop area is in RD New
                      pyproj.Proj(ds.crs.to_epsg() if ds.crs else 32631))  # The CRS as specified in the image
        crop_shape = shapely.ops.transform(tfm, crop_shape)
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
        transform = window_transform * window_transform.scale((window.width / data.shape[-1]),
                                                              (window.height / data.shape[-2]))
        # Apply geometry mask.
        geometry_mask = rasterio.features.geometry_mask([crop_shape], data[0].shape, transform)
        band_masked = np.ma.array(data[0], mask=geometry_mask, dtype=np.int16, fill_value=0)

        return band_masked


def main():
    aoi_json = get_study_area('./resources/study_area/Polygon.geojson')
    # load green band
    homegreen = "./resources/IMG_DATA/T31UFU_20210823T105031_B03.jp2"
    greenarray = get_image_data(homegreen, aoi_json)
    # # load NIR Band
    homenir = "./resources/IMG_DATA/T31UFU_20210823T105031_B08.jp2"
    nirarray = get_image_data(homenir, aoi_json)
    # load SWIR Data
    homeswir = "./resources/IMG_DATA/T31UFU_20210823T105031_B11.jp2"
    swirarray = get_image_data(homeswir, aoi_json, resample=greenarray.shape)

    NDMI_GAO = calculate_normalized_index(nirarray, swirarray)
    NDMI_McFeeters = calculate_normalized_index(greenarray, nirarray)
    ModifiedNDMI_Xu = calculate_normalized_index(greenarray, swirarray)

    show(NDMI_GAO, title='GAO NDWI', cmap='gist_ncar')
    show(ModifiedNDMI_Xu, title='ModifiedMDWI', cmap='gist_ncar')
    show(NDMI_McFeeters, title='MDWI McFeeters', cmap='gist_ncar')


if __name__ == '__main__':
    main()
