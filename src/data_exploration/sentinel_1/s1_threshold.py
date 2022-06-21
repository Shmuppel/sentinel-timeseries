"""
Date: Thursday 2022/06/16
Authors: Soria & Sotiris
Title: Calculate threshold (dB) based classification of pooling
"""

#           INSTRUCTIONS
# 1. Select a b-box (potential flooded parcel) [e.g. 10 parcels]
# 2. Find the min/max/stdv
# 3. Do that for at least 3 different images
# 4. Come up with threshold

#           Import packages
import rasterio, numpy, fiona, statistics
import geopandas as gpd
from osgeo import gdal
from rasterstats import zonal_stats
from zipfile import ZipFile
from src.util import get_study_area, get_image_data

# import matplotlib.pyplot as plt
# import rasterio.plot as rplt

# Sed directory
os.chdir('C:\Projects\pooling-detection')

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


#           Import Data
S1A_20200218_VH = 'resources/S1A_IW_GRDH_1SDV_20200218T172507_20200218T172532_031310_039A30_3336.zip'
S1A_20210619_VH = 'resources/S1A_IW_GRDH_1SDV_20210619T171711_20210619T171736_038412_048863_432B.zip'
S1A_20211022_VH = 'resources/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.zip'
output_dir = 'src/data_exploration/sentinel_1/temp_tiff'

# Extract tif files from a zip file
extract_tif_from_zip(S1A_20200218_VH, output_dir)
extract_tif_from_zip(S1A_20210619_VH, output_dir)
extract_tif_from_zip(S1A_20211022_VH, output_dir)
S1A_20200218_VH = gdal.Open(
    'src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20211017T171716_20211017T171741_040162_04C1B1_6C50.SAFE/measurement/s1a-iw-grd-vh-20200218t172507-20200218t172532-031310-039a30-002.tiff')
S1A_20210619_VH = gdal.Open(
    'src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.SAFE/measurement/s1a-iw-grd-vh-20210619t171711-20210619t171736-038412-048863-002.tiff')
S1A_20211022_VH = gdal.Open(
    'src/data_exploration/sentinel_1/temp_tiff/S1A_IW_GRDH_1SDV_20211017T171716_20211017T171741_040162_04C1B1_6C50.SAFE/measurement/s1a-iw-grd-vh-20211022t172522-20211022t172547-040235-04c439-002.tiff')

aoi = get_study_area("resources/study_area/Polygon.geojson")

#           1. Creating B-Box
# B-Box 1
bb_1 = 1079 # 2019-06-17 OBJECTID_1
# B-Box 2
bb_2 = 562 # 2019-06-22
# B-Box 3
bb_3 = 121 # 2020-03-26
# B-Box 4
bb_4= 1037 # 2021-10-24

#           2. Zonal Statistics /rasterstats/
zona_list_1 = zonal_stats("...shp...", "...tif...", stats="count min median mean max std")

#           3. Calculate Averages
averages = statistics.mean(var1, var2, var3)

#           3.1 Export results
# ??wright txt file??
