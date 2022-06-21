"""
Date: Thursday 2022/06/16
Authors: Sotiris
Title: Calculate threshold (dB) based classification of pooling
=================================================================
                        INSTRUCTIONS
1. Select a b-box (potential flooded parcel) [4 parcels]
2. Find the min/max/stdv
3. Do that for 3 different images/time events
4. Come up with threshold
"""

#           Import packages
import os
import numpy as np
import geopandas as gpd
from osgeo import gdal
from rasterstats import zonal_stats
from zipfile import ZipFile
from src.util import get_study_area, get_image_data

#           Sed directory
os.chdir(r'C:\Projects\pooling-detection')


def extract_tif_from_zip(zipfile_name, output_loc):
    # Extract all the tiff files from a specified zip folder
    with ZipFile(zipfile_name, 'r') as zipObj:
        list_of_file_names = zipObj.namelist()
        for fileName in list_of_file_names:
            if fileName.endswith('.tiff'):
                # Extract a single file from zip
                zipObj.extract(fileName, output_loc)
                print('The TIFF file is extracted in temp_tiff')


def warp_tif_files(im1, im2, im3):
    # Warp the tif files and safe to new tif
    output_raster_im1 = "src/data_exploration/sentinel_1/temp_tiff/im1_warp.tif"
    output_raster_im2 = "src/data_exploration/sentinel_1/temp_tiff/im2_warp.tif"
    output_raster_im3 = "src/data_exploration/sentinel_1/temp_tiff/im3_warp.tif"
    im1_w = gdal.Warp(output_raster_im1, im1, dstSRS="EPSG:4326")
    im2_w = gdal.Warp(output_raster_im2, im2, dstSRS="EPSG:4326")
    im3_w = gdal.Warp(output_raster_im3, im3, dstSRS="EPSG:4326")
    print('Files are warped')
    return im1_w, im2_w, im3_w


def convert_to_decibel(vh_warp):
    # Convert to dB
    vh_db = np.log10(vh_warp, out=np.zeros_like(vh_warp, dtype='float32'), where=(vh_warp != 0))
    vh_db = vh_db.astype('float16')
    print('Files are converted to dB')
    return vh_db


#           Import Data
# Filenames
image_1 = 'resources/S1A_IW_GRDH_1SDV_20200218T172507_20200218T172532_031310_039A30_3336.zip'
image_2 = 'resources/S1A_IW_GRDH_1SDV_20210619T171711_20210619T171736_038412_048863_432B.zip'
image_3 = 'resources/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.zip'
output_dir = 'src/data_exploration/sentinel_1/temp_tiff'

# Extract tif files from a zip file
extract_tif_from_zip(image_1, output_dir)
extract_tif_from_zip(image_2, output_dir)
extract_tif_from_zip(image_3, output_dir)
# Rasters
S1A_20200218_VH = gdal.Open('src/data_exploration/sentinel_1/temp_tiff'
                            '/S1A_IW_GRDH_1SDV_20200218T172507_20200218T172532_031310_039A30_3336.SAFE/measurement'
                            '/s1a-iw-grd-vh-20200218t172507-20200218t172532-031310-039a30-002.tiff')
S1A_20210619_VH = gdal.Open('src/data_exploration/sentinel_1/temp_tiff'
                            '/S1A_IW_GRDH_1SDV_20210619T171711_20210619T171736_038412_048863_432B.SAFE/measurement'
                            '/s1a-iw-grd-vh-20210619t171711-20210619t171736-038412-048863-002.tiff')
S1A_20211022_VH = gdal.Open('src/data_exploration/sentinel_1/temp_tiff'
                            '/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.SAFE/measurement'
                            '/s1a-iw-grd-vh-20211022t172522-20211022t172547-040235-04c439-002.tiff')
# Vectors
aoi = get_study_area("resources/study_area/Polygon.geojson")  # With function from util.py
parcels = gpd.read_file("resources/study_area/AOI_BRP_WGS84.geojson")
# %%
#                           Pre-Process
S1A_20200218_VH_warp, S1A_20210619_VH_warp, S1A_20211022_VH_warp = warp_tif_files(S1A_20200218_VH, S1A_20210619_VH,
                                                                                  S1A_20211022_VH)
S1A_20200218_VH_crop, geometry_1 = get_image_data("src/data_exploration/sentinel_1/temp_tiff/im1_warp.tif", aoi)
S1A_20200218_VH_db = convert_to_decibel(S1A_20200218_VH_crop)
masked_band1 = np.ma.array(S1A_20200218_VH_db, mask=S1A_20200218_VH_db.mask, dtype=np.float32, fill_value=-999.)  # 1
S1A_20200218_VH_db = masked_band1.filled()
S1A_20210619_VH_crop, geometry_2 = get_image_data("src/data_exploration/sentinel_1/temp_tiff/im2_warp.tif", aoi)
S1A_20210619_VH_db = convert_to_decibel(S1A_20210619_VH_crop)
masked_band2 = np.ma.array(S1A_20210619_VH_db, mask=S1A_20210619_VH_db.mask, dtype=np.float32, fill_value=-999.)  # 2
S1A_20210619_VH_db = masked_band2.filled()
S1A_20211022_VH_crop, geometry_3 = get_image_data("src/data_exploration/sentinel_1/temp_tiff/im3_warp.tif", aoi)
S1A_20211022_VH_db = convert_to_decibel(S1A_20211022_VH_crop)
masked_band3 = np.ma.array(S1A_20211022_VH_db, mask=S1A_20211022_VH_db.mask, dtype=np.float32, fill_value=-999.)  # 3
S1A_20211022_VH_db = masked_band3.filled()

#           1. Creating B-Box
# S2 Dates 2019-06-17, 2019-06-22, 2020-03-26, 2021-10-24
bbox = parcels.loc[parcels['OBJECTID_1'].isin([1079, 562, 121, 1037]), :]

# %%
#           2. Zonal Statistics /rasterstats/
# for loop
stats_20200218 = zonal_stats(bbox, S1A_20200218_VH_db,
                             stats="count min median mean max std",
                             affine=geometry_1,
                             nodata=-999.)

stats_20210619 = zonal_stats(bbox, S1A_20200218_VH_db,
                             stats="count min median mean max std",
                             affine=geometry_1,
                             nodata=-999.)

stats_20211022 = zonal_stats(bbox, S1A_20200218_VH_db,
                             stats="count min median mean max std",
                             affine=geometry_1,
                             nodata=-999.)

# %%
#           3. Calculate Averages
min1 = 0. ; max1 = 0. ; mean = 0. ; count = 0. ; std = 0. ; median = 0.

for elem in range(len(stats_20200218)):
    for key in stats_20200218[elem]:
        if key == 'min':
            min1 += stats_20200218[elem]['min']
        elif key == 'max':
            max1 += stats_20200218[elem]['max']
        elif key == 'mean':
            mean += stats_20200218[elem]['mean']
        elif key == 'count':
            count += stats_20200218[elem]['count']
        elif key == 'std':
            std += stats_20200218[elem]['std']
        elif key == 'median':
            median += stats_20200218[elem]['median']

min1 = round(min1 / 4., 4) ; print('Min: ', min1)
max1 = round(max1 / 4., 4) ; print('Max: ', max1)
mean = round(mean / 4., 4) ; print('Mean: ', mean)
count = round(count / 4., 4) ; print('Count: ', count)
std = round(std / 4., 4) ; print('Std: ', std)
median = round(median / 4., 4) ; print('Median: ', median)
