"""
Title: Create composite RGB with (Dry, Dry, Wet) for (ponding) change visualization
Credit: Reverse-engineered code of Soria's s1_rgb_edited.py
Date: 2022/06/20 | Author: Sotiris
"""
# Imort Packages
import numpy as np
from osgeo import gdal
from zipfile import ZipFile
from rasterio.plot import show
from src.util import get_study_area, get_image_data

#  Extract .tif from zip
def extract_tif_from_zip(zipfile_name, output_loc):
    # Extract all the tiff files from a specified zip folder
    with ZipFile(zipfile_name, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        for fileName in listOfFileNames:
            if fileName.endswith('.tiff'):
                # Extract a single file from zip
                zipObj.extract(fileName, output_loc)
                print('The TIFF file is extracted in temp_tiff')

# Warp the tif files and safe to new tif
def warp_tif_files(raster, output_raster):
    output_r = 'src/data_exploration/sentinel_1/temp_tiff/vv_warp.tif'
    output_raster_vh = "src/data_exploration/sentinel_1/temp_tiff/vh_warp.tif"
    # vv_warp = gdal.Warp(output_raster_vv, vv_backscatter, dstSRS="EPSG:4326")
    vh_warp = gdal.Warp(output_raster_vh, vh_backscatter, dstSRS="EPSG:4326")
    print('Files are warped')
    return vh_warp # ,vv_warp

# Convert to dB
def convert_to_decibel(vh_warp): # ,vv_warp
    # vv_db = np.log10(vv_warp, out=np.zeros_like(vv_warp, dtype='float32'), where=(vv_warp != 0))
    vh_db = np.log10(vh_warp, out=np.zeros_like(vh_warp, dtype='float32'), where=(vh_warp != 0))
    print('Files are converted to dB')
    return vh_db # ,vv_db

# Min-Max normalization for RGB
def min_max_norm(band):
    band_min, band_max = band.min(), band.max()
    return (band - band_min) / (band_max - band_min)

# Create Stack Array
def stack_arrays(Dry, Dry, Wet):
    s1_rgb = np.stack((Dry, Dry, Wet))
    print('Stack rgb done')
    return s1_rgb



def main():
    zip_name_dry = 'S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip'
    zip_name_wet = '...'
    output_dry = 'src/data_exploration/sentinel_1/temp_tiff'
    output_wet = '...'

    # Extract tif files from a zip file
    extract_tif_from_zip(zip_name_dry, output_dry)  # Dry
    extract_tif_from_zip(zip_name_wet, output_wet)  # Wet

    # Open with gdal
    # vv_backscatter = gdal.Open('src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement/s1a-iw-grd-vv-20210823t172521-20210823t172546-039360-04a618-001.tiff')
    vh_backscatter = gdal.Open('src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement/s1a-iw-grd-vh-20210823t172521-20210823t172546-039360-04a618-002.tiff')

    # Warp to epsg 4326
    # vv_warped = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vv_warp.tiff', vv_backscatter, dstSRS="EPSG:4326")
    # print('vv files are warped')
    vh_warped = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vh_warp.tiff', vh_backscatter, dstSRS="EPSG:4326") # Dry
    vh_warped = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vh_warp.tiff', vh_backscatter, dstSRS="EPSG:4326") # Wet
    print('vh files are warped')

    # get study area
    study_area = get_study_area("resources/study_area/Polygon.geojson")

    # get image data from warped tif files
    # vv = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vv_warp.tiff", study_area)
    vh = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vh_warp.tiff", study_area)
    print('Image data study area acquired')

    # convert arrays to decibels
    vh_db = convert_to_decibel(vh) # Dry
    vh_db = convert_to_decibel(vh) # Wet



    vh_db_norm = min_max_norm(vh_db) # Dry
    vh_db_norm = min_max_norm(vh_db) # Wet
    print('Normalise the three bands')

    # stack VV, VH, RATIO becomes a ndarray
    s1_rgb = stack_arrays(Dry, Dry, Wet)
    show(s1_rgb)


if __name__ == '__main__':
    main()
