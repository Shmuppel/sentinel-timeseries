"""
Title: Create composite RGB with (Dry, Dry, Wet) for (ponding) change visualization
Credit: Reverse-engineered code of Soria's s1_rgb_edited.py
Date: 2022/06/20 | Author: Sotiris
"""
# Import Packages
import os
import numpy as np
import rasterio
from PIL import Image
from matplotlib import pyplot as plt
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

### Create Warp function
# def warp_tif_files(raster, output_raster):
#     # Warp the tif files and safe to new tif
#     output_r = 'src/data_exploration/sentinel_1/temp_tiff/vv_warp.tif'
#     output_raster_vh = "src/data_exploration/sentinel_1/temp_tiff/vh_warp.tif"
#     vv_warp = gdal.Warp(output_raster_vv, vv_backscatter, dstSRS="EPSG:4326")
#     vh_warp = gdal.Warp(output_raster_vh, vh_backscatter, dstSRS="EPSG:4326")
#     print('Files are warped')
#     return vv_warp, vh_warp

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
def stack_arrays(Dry, Wet):
    s1_rgb = np.stack((Dry, Dry, Wet))
    print('Stack rgb done')
    return s1_rgb


def main():
    zip_name_dry = 'resources/S1A_IW_GRDH_1SDV_20211017T171716_20211017T171741_040162_04C1B1_6C50.zip'
    zip_name_wet = 'resources/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.zip'
    output_dir = 'src/data_exploration/sentinel_1/temp_tiff'

    # Extract tif files from a zip file
    extract_tif_from_zip(zip_name_dry, output_dir)  # Dry
    extract_tif_from_zip(zip_name_wet, output_dir)  # Wet

    # Open with gdal
    # vv_backscatter = gdal.Open('src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement/s1a-iw-grd-vv-20210823t172521-20210823t172546-039360-04a618-001.tiff')
    vh_backscatter_dry = gdal.Open('src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20211017T171716_20211017T171741_040162_04C1B1_6C50.SAFE/measurement/s1a-iw-grd-vh-20211017t171716-20211017t171741-040162-04c1b1-002.tiff')
    vh_backscatter_wet = gdal.Open('src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.SAFE/measurement/s1a-iw-grd-vh-20211022t172522-20211022t172547-040235-04c439-002.tiff')

    # Warp to epsg 4326
    # vv_warped = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vv_warp.tiff', vv_backscatter, dstSRS="EPSG:4326")
    # print('vv files are warped')
    vh_warped_dry = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vh_warp_dry.tiff', vh_backscatter_dry, dstSRS="EPSG:4326") # Dry
    vh_warped_wet = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vh_warp_wet.tiff', vh_backscatter_wet, dstSRS="EPSG:4326") # Wet
    print('vh files are warped')

    # get study area
    study_area = get_study_area("resources/study_area/Polygon.geojson")

    # get image data from warped tif files
    # vv = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vv_warp.tiff", study_area)
    vh_dry = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vh_warp_dry.tiff", study_area) # Dry
    vh_wet = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vh_warp_wet.tiff", study_area, vh_dry.shape) # Wet
    print('Image data study area acquired')

    # convert arrays to decibels and then normalize
    vh_db_dry = convert_to_decibel(vh_dry) # Dry
    vh_db_wet = convert_to_decibel(vh_wet) # Wet
    vh_db_norm_dry = min_max_norm(vh_db_dry) # Dry
    vh_db_norm_wet = min_max_norm(vh_db_wet) # Wet
    print('Normalise the three bands')
    # breakpoint()
    # stack VH, VH, Dry becomes a ndarray
    s1_rgb = stack_arrays(vh_db_norm_dry, vh_db_norm_wet) # (Dry, Dry, Wet)
    show(s1_rgb)
    with rasterio.open('Image.tif', 'w', driver='GTiff', width=1080, height=720, count=3, dtype=s1_rgb.dtype) as tile:
        tile.write(s1_rgb)

os.chdir('C:\Projects\pooling-detection')
if __name__ == '__main__':
    main()
