"""
Title: Clip to AOI and select partials
Author: Sotiris Kechagias (MasterHydro) et al
Date: 2022/06/14 (Tue)
"""

# Import Packages
import os
import fiona
from osgeo import gdal
import geopandas as gpd
from matplotlib import pyplot as plt
import rasterio
from rasterio.mask import mask
from fiona.crs import from_epsg
from pyproj import Proj, transform

import numpy as np
from rasterio.plot import show

# Create directories
if os.path.exists('Data'):
    pass
else:
    os.makedirs('Data')

# Create directories
if os.path.exists('Export'):
    pass
else:
    os.makedirs('Export')

# Import Data
#   Raster / Images
band1 = gdal.Open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")
band1_1 = rasterio.open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")

# how to create a stack
#### https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_raster_stack_crop.html ####

#   Shapefiles
# Geopandas style
AOI_GDF = gpd.read_file('./resources/study_area/Polygon.geojson')
crs = 32631
AOI_GDF = AOI_GDF.to_crs(epsg=crs)
AOI_GDF.plot()
plt.show()
# Fiona style that works in the following band mask
aoiFile = fiona.open('./resources/study_area/Polygon.geojson')
aoiGeom = [aoiFile[0]['geometry']]
# #%%
#
# #get band names
# bandPath = './Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA'
# bandNames = os.listdir(bandPath)
# print(bandNames)
#
# # clip all bands
# for band in bandNames:
#     rasterPath = os.path.join(bandPath, band)
#     rasterBand = rasterio.open(rasterPath)
#     outImage, outTransform = mask(rasterBand, AOI_GDF, crop=True)
#     outMeta = rasterBand.meta
#     outMeta.update({"driver": 'GTiff',
#                     "height": outImage.shape[1],
#                     "width": outImage.shape[2],
#                     "transform": outTransform})
#     outPath = os.path.join('./Export', band)
#     outRaster = rasterio.open(outPath, "w", **outMeta)
#     outRaster.write(outImage)
#     outRaster.close()
