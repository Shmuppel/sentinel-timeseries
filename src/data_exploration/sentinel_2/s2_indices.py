from rasterio.plot import show
from src.util import *


def calculate_indices():
    aoi_json = get_study_area('resources/study_area/Polygon.geojson')
    # load green band
    green_image = "resources/images/IMG_DATA/T31UFU_20210823T105031_B03.jp2"
    green_array, geometry_transform = get_image_data(green_image, aoi_json)
    # # load NIR Band
    nir_image = "resources/images/IMG_DATA/T31UFU_20210823T105031_B08.jp2"
    nir_array,_ = get_image_data(nir_image, aoi_json)
    # load SWIR Data
    swir_image = "resources/images/IMG_DATA/T31UFU_20210823T105031_B11.jp2"
    swir_array,_ = get_image_data(swir_image, aoi_json, resample=green_array.shape)

    ndwi_gao = calculate_normalized_index(nir_array, swir_array)
    ndwi_mcfeeters = calculate_normalized_index(green_array, nir_array)
    mndwi_xu = calculate_normalized_index(green_array, swir_array)

    #show(ndwi_gao, title='NDWI GAO', cmap='gist_ncar')
    #show(ndwi_mcfeeters, title='NDWI McFeeters', cmap='gist_ncar')
    #show(mndwi_xu, title='MNDWI', cmap='gist_ncar')

    return ndwi_gao, ndwi_mcfeeters, mndwi_xu, geometry_transform

if __name__ == '__main__':
    calculate_indices()
