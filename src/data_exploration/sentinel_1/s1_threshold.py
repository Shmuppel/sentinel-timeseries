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
import os, rasterio, numpy, fiona, statistics
import geopandas as gpd
from osgeo import gdal
from rasterstats import zonal_stats
from zipfile import ZipFile
from src.util import get_study_area, get_parcels

#           Sed directory
os.chdir(r'C:\Projects\pooling-detection')


# Extract .tif from zip
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
aoi = get_study_area("resources/study_area/Polygon_WGS84.geojson")  # With function from util.py
parcels = gpd.read_file("resources/study_area/AOI_BRP_WGS84.geojson")

#           1. Creating B-Box
bb_1 = parcels[parcels.OBJECTID_1 == 1079]  # 2019-06-17
bb_2 = parcels[parcels.OBJECTID_1 == 562]   # 2019-06-22
bb_3 = parcels[parcels.OBJECTID_1 == 121]   # 2020-03-26
bb_4 = parcels[parcels.OBJECTID_1 == 1037]  # 2021-10-24

# %%
#           2. Zonal Statistics /rasterstats/
# for loop
bb1_stats = zonal_stats([bb_1, bb_2, bb_3, bb_4], "...tif...", stats="count min median mean max std")

#           3. Calculate Averages
averages = statistics.mean(var1, var2, var3)

#           3.1 Export results
# ??wright txt file??
