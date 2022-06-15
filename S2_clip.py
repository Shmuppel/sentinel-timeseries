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

import numpy as np
from rasterio.plot import show

# Create directories
if os.path.exists('Data'):
    pass
else:
    os.makedirs('Data')

# Import Data
#   Raster / Images
band1 = gdal.Open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")
band1_1 = rasterio.open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")

# how to create a stack
#### https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_raster_stack_crop.html ####

#   Shapefiles
AOI_GDF = gpd.read_file('./resources/study_area/Polygon.geojson')
crs = 4326
AOI_GDF = AOI_GDF.to_crs(epsg=crs)
AOI_GDF.plot(aspect=1)
plt.show() # Problem with plot ValueError: 'box_aspect' and 'fig_aspect' must be positive



# %%

#get band names
bandPath = './Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA'
bandNames = os.listdir(bandPath)
print(bandNames)

# clip all bands
for band in bandNames:
    rasterPath = os.path.join(bandPath, band)
    rasterBand = rasterio.open(rasterPath)
    outImage, outTransform = mask(rasterBand, AOI_GDF, crop=True)
    outMeta = rasterBand.meta
    outMeta.update({"driver": 'JP2OpenJPEG',
                    "height": outImage.shape[1],
                    "width": outImage.shape[2],
                    "transform": outTransform})
    outPath = os.path.join('./rst', band)
    outRaster = rasterio.open(outPath, "w", **outMeta)
    outRaster.write(outImage)
    outRaster.close()
#%%
