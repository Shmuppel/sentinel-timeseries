import os
from zipfile import ZipFile

import numpy as np
from osgeo import gdal
from rasterio.plot import show

from src.util import get_study_area, get_image_data


#### Links to Sentinel 1 images ####
# Link to Sentinel 1 Image 23-08-2021 from SentinelHub
# s3://sentinel-s1-l1c/GRD/2021/8/23/IW/DV/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894/

# I downloaded one S1 tile from https://search.asf.alaska.edu/#/?zoom=7.252&center=9.200,52.727&polygon=POLYGON((5.5751%2052.986,5.8622%2052.986,5.8622%2053.1695,5.5751%2053.1695,5.5751%2052.986))&start=2021-08-21T22:00:00Z&end=2021-08-24T21:59:59Z&flightDirs=Ascending&resultsLoaded=true&granule=S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894-GRD_HD
# https://appdividend.com/2022/01/19/python-unzip/#:~:text=To%20unzip%20a%20file%20in,inbuilt%20python%20module%20called%20zipfile.


def extract_tif_from_zip(zipfile_name, output_loc):
    # Extract all the tiff files from a specified zip folder
    with ZipFile(zipfile_name, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            if fileName.endswith('.tiff'):
                # Extract a single file from zip
                zipObj.extract(fileName, output_loc)
                print('The TIFF file is extracted in temp_tiff')


def warp_tif_files(raster, output_raster):
    # Warp the tif files and safe to new tif
    output_r = 'src/data_exploration/sentinel_1/temp_tiff/vv_warp.tif'
    output_raster_vh = "src/data_exploration/sentinel_1/temp_tiff/vh_warp.tif"
    vv_warp = gdal.Warp(output_raster_vv, vv_backscatter, dstSRS="EPSG:4326")
    vh_warp = gdal.Warp(output_raster_vh, vh_backscatter, dstSRS="EPSG:4326")
    print('Files are warped')
    return vv_warp, vh_warp


def convert_to_decibel(vv_warp, vh_warp):
    # Convert to dB
    vv_db = np.log10(vv_warp, out=np.zeros_like(vv_warp, dtype='float32'), where=(vv_warp != 0))
    vh_db = np.log10(vh_warp, out=np.zeros_like(vh_warp, dtype='float32'), where=(vh_warp != 0))
    print('Files are converted to dB')
    return vv_db, vh_db


def calculate_ratio(vv_db, vh_db):
    # Calculate vv-vh ratio
    vv_vh_ratio = vv_db - vh_db
    # Check if it works
    assert np.min(vv_vh_ratio) != -np.inf
    print('Calculate ratio done')
    return vv_vh_ratio


def stack_arrays(vv_db, vh_db, vv_vh_ratio):
    # Create stack of vv, vh, vv/vh
    s1_rgb = np.stack((vv_db, vh_db, vv_vh_ratio))
    print('Stack rgb done')
    return s1_rgb


def min_max_norm(band):
    band_min, band_max = band.min(), band.max()
    return (band - band_min) / (band_max - band_min)


def main():
    zip_name = 'E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip'
    output_folder = 'src/data_exploration/sentinel_1/temp_tiff'

    # extract tif files from a zip file
    # extract_tif_from_zip(zip_name, output_folder)

    # open with gdal
    #vv_backscatter = gdal.Open('../../../resources/images/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement/s1a-iw-grd-vv-20210823t172521-20210823t172546-039360-04a618-001.tiff')
    #vh_backscatter = gdal.Open('../../../resources/images/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement/s1a-iw-grd-vh-20210823t172521-20210823t172546-039360-04a618-002.tiff')

    # warp to epsg 4326
    #vv_warped = gdal.Warp('../../../resources/images/warped_vv.tiff', vv_backscatter, dstSRS="EPSG:4326")
    #vh_warped = gdal.Warp('../../../resources/images/warped_vh.tiff', vh_backscatter, dstSRS="EPSG:4326")

    # get study area
    study_area = get_study_area("../../../resources/study_area/Polygon.geojson")
    # get image data from warped tif files
    vv = get_image_data("../../../resources/images/warped_vv.tiff", study_area)
    vh = get_image_data("../../../resources/images/warped_vh.tiff", study_area)

    # convert arrays to decibels
    vv_db, vh_db = convert_to_decibel(vv, vh)
    # calculate VV / VH ratio
    vv_vh_ratio = calculate_ratio(vv_db, vh_db)

    vv_db_norm = min_max_norm(vv_db)
    vh_db_norm = min_max_norm(vh_db)
    ratio_norm = min_max_norm(vv_vh_ratio)

    # stack VV, VH, RATIO becomes a ndarray
    s1_rgb = stack_arrays(vv_db_norm, vh_db_norm, ratio_norm)
    show(s1_rgb)


if __name__ == '__main__':
    main()
