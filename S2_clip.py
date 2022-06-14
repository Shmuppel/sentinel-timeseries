"""
Title: Clip to AOI and select partials
Author: Sotiris Kechagias (MasterHydro) et al
Date: 2022/06/14 (Tue)
"""

# Import Packages
import os
from osgeo import gdal
import geopandas as gpd
from matplotlib import pyplot as plt
import rasterio
import numpy as np
from rasterio import plot

# Create directories
if not os.path.exists('Data'): os.makedirs('Data')

# Import Data
#   Raster / Images

# Create a data directory within the directory where this script is run if it does not exist yet and store file
# bands = r'./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/'
band1 = gdal.Open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")
band1_1 = rasterio.open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")


# how to create a stack
#### https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_raster_stack_crop.html ####

#   Shapefiles
jsonGDF = gpd.read_file('./Data/Polygon.geojson')

# Transform AOI crs to Sentinel crs
project_crs = 4326  # Sentinels CRS
jsonGDF = jsonGDF.to_crs(epsg=project_crs)
jsonGDF.plot(aspect=1)
plt.show()
