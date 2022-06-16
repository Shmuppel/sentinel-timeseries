#### Import Packages ####
from zipfile import ZipFile
from osgeo import gdal
import os
import numpy as np
from matplotlib import pyplot as plt


#### Links to Sentinel 1 images ####
#Link to Sentinel 1 Image 23-08-2021 from SentinelHub
# s3://sentinel-s1-l1c/GRD/2021/8/23/IW/DV/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894/

# I downloaded one S1 tile from https://search.asf.alaska.edu/#/?zoom=7.252&center=9.200,52.727&polygon=POLYGON((5.5751%2052.986,5.8622%2052.986,5.8622%2053.1695,5.5751%2053.1695,5.5751%2052.986))&start=2021-08-21T22:00:00Z&end=2021-08-24T21:59:59Z&flightDirs=Ascending&resultsLoaded=true&granule=S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894-GRD_HD
# https://appdividend.com/2022/01/19/python-unzip/#:~:text=To%20unzip%20a%20file%20in,inbuilt%20python%20module%20called%20zipfile.


from src.util import get_study_area, get_image_data

def extract_tif_from_zip(zipfile_name, output_loc):
    # Extract all the tiff files from a specified zip folder
    with ZipFile(zipfile_name, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            if fileName.endswith('.tiff'):
                # Extract a single file from zip
                zipObj.extract(fileName, output_loc)
                print('The TIFF file is extracted in temp_tiff')


def open_tif_files(output_loc):
    # Open the tif files using GDAL and warp them to WGS84
    dirname = 'src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement'
    vv_name = 's1a-iw-grd-vv-20210823t172521-20210823t172546-039360-04a618-001.tiff'
    vh_name = 's1a-iw-grd-vh-20210823t172521-20210823t172546-039360-04a618-002.tiff'
    vv_backscatter = gdal.Open(os.path.join(dirname, vv_name))
    vh_backscatter = gdal.Open(os.path.join(dirname, vh_name))
    print('Opening tiff files')
    return vv_backscatter, vh_backscatter


def warp_tif_files(vv_backscatter, vh_backscatter):
    # Warp the tif files and safe to new tif
    output_raster_vv = 'src/data_exploration/sentinel_1/temp_tiff/vv_warp.tif'
    output_raster_vh = "src/data_exploration/sentinel_1/temp_tiff/vh_warp.tif"
    vv_warp = gdal.Warp(output_raster_vv, vv_backscatter, dstSRS="EPSG:4326")
    vh_warp = gdal.Warp(output_raster_vh, vh_backscatter, dstSRS="EPSG:4326")
    print('Files are warped')
    return vv_warp, vh_warp


def convert_to_decibel(vv_warp, vh_warp):
    # Convert to dB
    vv_db = np.log10(vv_warp, out=np.zeros_like(vv_warp, dtype='float32'), where=(vv_warp != 0))
    vh_db = np.log10(vh_warp, out=np.zeros_like(vh_warp, dtype='float32'), where=(vh_warp != 0))
    vv_db = vv_db.astype('float16')
    vh_db = vh_db.astype('float16')
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
    s1_rgb = np.dstack((vv_db, vh_db, vv_vh_ratio))
    print('Stack rgb done')
    return s1_rgb


zip_name = 'E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip'
output_folder = 'src/data_exploration/sentinel_1/temp_tiff'



def main():
    # extract tif files from a zip file
    #extract_tif_from_zip(zip_name, output_folder)

    # open tif files with gdal
    #vv_backscatter, vh_backscatter = open_tif_files(output_folder)

    # Warp to epsg 4326
    #vv_warp, vh_warp = warp_tif_files(vv_backscatter, vh_backscatter)

    # get study area
    study_area = get_study_area("resources/study_area/Polygon.geojson")

    # get image data from warped tif files
    vv = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vv_warp.tif", study_area)
    vh = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vh_warp.tif", study_area)

    # convert arrays to decibels
    vv_db, vh_db = convert_to_decibel(vv, vh)
    breakpoint()
    # calculate VV / VH ratio
    vv_vh_ratio = calculate_ratio(vv_db, vh_db)

    # stack VV, VH, RATIO becomes a ndarray
    s1_rgb = stack_arrays(vv_db, vh_db, vv_vh_ratio)

    plt.imshow(s1_rgb)
    plt.show()

if __name__ == '__main__':
    main()


