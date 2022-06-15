# A code that calculates the Indices based on downloaded Sentinel 2 data
import json
from typing import *
import rasterio
import numpy as np
import geopandas as gpd
import shapely
from rasterio.plot import show
from rasterio.enums import Resampling
from shapely.ops import transform
import rasterio.features
def calculate_normalized_index(band1, band2):
    """
     Returns Indices based on the function call.
     """
    return (band1 - band2) / (band1 + band2)


def get_study_area():
    """ """
    aoi = gpd.read_file('./resources/study_area/Polygon.geojson', rows=1)
    aoi = aoi.to_crs(epsg=4326)
    aoi_json = json.loads(aoi.to_json())
    return aoi_json['features'][0]['geometry']


def get_image_data(
        image_path: str,
        zone,
        resample = None
):
    """
  image_path: Opens a image using rasterIO given an image path.
  zone: Clips the image to the zone, this should be some kind of Polygon.
  resample: Resamples the image to given dimensions.
  """
    with rasterio.open(image_path) as ds:
        epsg = ds.crs.to_epsg() if ds.crs else 32631
        breakpoint()
        zone_transformed = zone.transform(epsg, clone=True)
        zone_polygon = shapely.geometry.shape(json.loads(zone_transformed.geojson))
        breakpoint()
        # Crop raster -- get bounding window of shape(s) in raster.
        window = rasterio.features.geometry_window(ds, [zone])
        window_transform = ds.window_transform(window)
        # Either set a new shape for the data or use the window's shape.
        shape = (resample[0], resample[1]) if isinstance(resample, tuple) else (window.height, window.width)

        # Limit raster to window, apply resampling if desired.
        data = ds.read(
            out_shape=shape,
            window=window,
            resampling=Resampling.cubic
        )

        # We have to transform the window (our cropped view) to a resampled view if we resampled.
        transform = window_transform * window_transform.scale((window.width / data.shape[-1]),
                                                              (window.height / data.shape[-2]))
        # Apply geometry mask.
        geometry_mask = rasterio.features.geometry_mask([zone_polygon], data[0].shape, transform)
        band_masked = np.ma.array(data[0], mask=geometry_mask, dtype=np.int16, fill_value=0)

        return band_masked


def main():
    aoi_json = get_study_area()
    # load green band
    homegreen = "resources/images/S2A_MSIL1C_20210823T105031_N0301_R051_T31UFU_20210823T144408.SAFE/GRANULE/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B03.jp2"
    greenarray = get_image_data(homegreen, aoi_json)
    rasterio.plot.show(greenarray)
    breakpoint()
    # # load NIR Band
    # homenir = "resources/images/S2A_MSIL1C_20210823T105031_N0301_R051_T31UFU_20210823T144408.SAFE/GRANULE/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B08.jp2"
    # nirarray = get_image_data(homenir, )
    #
    # # load SWIR Data
    # homeswir = "resources/images/S2A_MSIL1C_20210823T105031_N0301_R051_T31UFU_20210823T144408.SAFE/GRANULE/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B11.jp2"
    # swirarray = get_image_data(homeswir, resample=greenarray.shape)


if __name__ == '__main__':
    main()

# # Calls the finction that calculates the indices.
# NDMI_GAO = calculate_normalized_index(nirarray, swirarray)
# ModifiedNDMI_Xu = calculate_normalized_index(greenarray, swirarray)
# NDMI_McFeeters = calculate_normalized_index(greenarray, nirarray)
#
# # Show indice map
# # rasterio.plot.show(NDMI_GAO)
#
# # #print(green.meta)
# show(NDMI_GAO, title='GAO NDWI', cmap='gist_ncar')
# # #print(nir.meta)
# show(ModifiedNDMI_Xu, title='ModifiedMDWI', cmap='gist_ncar')
# # #print(swir.meta)
# show(NDMI_McFeeters, title='MDWI McFeeters', cmap='gist_ncar')
