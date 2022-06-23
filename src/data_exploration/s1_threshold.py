"""
Title: Calculate threshold (dB) based classification of pooling
Date: Thursday 2022/06/16 | Authors: Sotiris
"""

#                   Import packages
import os
import numpy as np
import geopandas as gpd
from osgeo import gdal
from rasterstats import zonal_stats
from zipfile import ZipFile
from src.util import get_study_area, get_image_data, s1_stats, plot1_indices

# Sed directory
os.chdir(r'C:\Projects\pooling-detection')


# Create functions
def pond_mask(image, pond):
    masked_band = np.ma.array(image,
                              mask=(pond | image.mask),
                              dtype=np.float32, fill_value=-999.)
    pond_m = masked_band.filled()
    return pond_m


def stats_calc(image, geometry, parcels):
    stats = zonal_stats(parcels,
                        image,
                        stats="count min median mean max std",
                        affine=geometry,
                        nodata=-999.)
    print('Done')
    return stats


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


# %%                Import Filenames/Paths
image_1, image_2, image_3 = './resources/S1A_IW_GRDH_1SDV_20200218T172507_20200218T172532_031310_039A30_3336.zip', \
                            './resources/S1A_IW_GRDH_1SDV_20210619T171711_20210619T171736_038412_048863_432B.zip', \
                            './resources/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.zip '
output_dir = './src/data_exploration/sentinel_1/temp_tiff'
#                   Extract tif files from a zip file
extract_tif_from_zip(image_1, output_dir)
extract_tif_from_zip(image_2, output_dir)
extract_tif_from_zip(image_3, output_dir)
#                   Import Images
S1A_20200218_VH = gdal.Open('./src/data_exploration/sentinel_1/temp_tiff'
                            '/S1A_IW_GRDH_1SDV_20200218T172507_20200218T172532_031310_039A30_3336.SAFE/measurement'
                            '/s1a-iw-grd-vh-20200218t172507-20200218t172532-031310-039a30-002.tiff')  # 1st Image
S1A_20210619_VH = gdal.Open('./src/data_exploration/sentinel_1/temp_tiff'
                            '/S1A_IW_GRDH_1SDV_20210619T171711_20210619T171736_038412_048863_432B.SAFE/measurement'
                            '/s1a-iw-grd-vh-20210619t171711-20210619t171736-038412-048863-002.tiff')  # 2nd Image
S1A_20211022_VH = gdal.Open('./src/data_exploration/sentinel_1/temp_tiff'
                            '/S1A_IW_GRDH_1SDV_20211022T172522_20211022T172547_040235_04C439_981A.SAFE/measurement'
                            '/s1a-iw-grd-vh-20211022t172522-20211022t172547-040235-04c439-002.tiff')  # 3rd Image
#                   Import Vectors
aoi = get_study_area("./resources/study_area/Polygon.geojson")
parcels = gpd.read_file("./resources/study_area/AOI_BRP_WGS84.geojson")
# %%                0. Pre-Process
# Warp images to CRS
S1A_20200218_VH_warp, S1A_20210619_VH_warp, S1A_20211022_VH_warp = warp_tif_files(S1A_20200218_VH,
                                                                                  S1A_20210619_VH,
                                                                                  S1A_20211022_VH)
S1A_20200218_VH_crop, geometry_1 = get_image_data("./src/data_exploration/sentinel_1/temp_tiff/im1_warp.tif", aoi)
S1A_20210619_VH_crop, geometry_2 = get_image_data("./src/data_exploration/sentinel_1/temp_tiff/im2_warp.tif", aoi)
S1A_20211022_VH_crop, geometry_3 = get_image_data("./src/data_exploration/sentinel_1/temp_tiff/im3_warp.tif", aoi)
# Convert to dB
S1A_20200218_VH_db, S1A_20210619_VH_db, S1A_20211022_VH_db = convert_to_decibel(S1A_20200218_VH_crop), \
                                                             convert_to_decibel(S1A_20210619_VH_crop), \
                                                             convert_to_decibel(S1A_20211022_VH_crop)
# Mask non-values -999.
masked_band1, masked_band2, masked_band3 = np.ma.array(S1A_20200218_VH_db, mask=S1A_20200218_VH_db.mask,
                                                       dtype=np.float32, fill_value=-999.), \
                                           np.ma.array(S1A_20210619_VH_db, mask=S1A_20210619_VH_db.mask,
                                                       dtype=np.float32, fill_value=-999.), \
                                           np.ma.array(S1A_20211022_VH_db, mask=S1A_20211022_VH_db.mask,
                                                       dtype=np.float32, fill_value=-999.)
# Create masks
S1A_20200218_VH_db_m, S1A_20210619_VH_db_m, S1A_20211022_VH_db_m = masked_band1.filled(), \
                                                                   masked_band2.filled(), \
                                                                   masked_band3.filled()

# %%                 1. Creating B-Box
# S2 Dates: 2019-06-17, 2019-06-22, 2020-03-26, 2021-10-24
bbox = parcels.loc[parcels['OBJECTID_1'].isin([1079, 562, 121, 1037]), :]

#                   2. Zonal Statistics
stats_20200218 = stats_calc(S1A_20200218_VH_db_m, geometry_1, bbox)
stats_20210619 = stats_calc(S1A_20210619_VH_db_m, geometry_2, bbox)
stats_20211022 = stats_calc(S1A_20211022_VH_db_m, geometry_3, bbox)

# %%                3. Calculate Averages
min1, max1, mean, count, std, median = 0., 0., 0., 0., 0., 0.
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
min1, max1, mean, count, std, median = round(min1 / 4., 4), round(max1 / 4., 4), round(mean / 4., 4), \
                                       round(count / 4., 4), round(std / 4., 4), round(median / 4., 4)
print('Min: ', min1, 'Max: ', max1, 'Mean: ', mean, '\nCount: ', count, 'Std: ', std, 'Median: ', median)

# %%                4. VISUALISE BASED ON THRESHOLDS
# Apply indices
pond20200218, pond20210619, pond20211022 = np.logical_and(S1A_20200218_VH_db >= min1, S1A_20200218_VH_db <= max1), \
                                           np.logical_and(S1A_20210619_VH_db >= min1, S1A_20210619_VH_db <= max1), \
                                           np.logical_and(S1A_20211022_VH_db >= min1, S1A_20211022_VH_db <= max1)
# Mask parcels based on indices
pond20200218_m, pond20210619_m, pond20211022_m = pond_mask(S1A_20200218_VH_db, pond20200218), \
                                                 pond_mask(S1A_20210619_VH_db, pond20210619), \
                                                 pond_mask(S1A_20211022_VH_db, pond20211022)
# Calculate the stats for all parcels
full_stats_20200218, full_stats_20210619, full_stats_20211022 = stats_calc(pond20200218_m, geometry_1, parcels), \
                                                                stats_calc(pond20210619_m, geometry_2, parcels), \
                                                                stats_calc(pond20211022_m, geometry_3, parcels)
#%% Calculate counts of count & Plot the count of the poonding pixels
s1_stats(full_stats_20200218, parcels, 'pooling_px')
plot1_indices(parcels, 'counts_pooling_px', '2020-02-18 ')
s1_stats(full_stats_20210619, parcels, 'pooling_pixels')
plot1_indices(parcels, 'counts_pooling_px', '2021-06-19 ')
s1_stats(full_stats_20211022, parcels, 'pooling_pixels')
plot1_indices(parcels, 'counts_pooling_px', '2021-10-22 ')
