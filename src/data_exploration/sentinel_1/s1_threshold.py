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

# import matplotlib.pyplot as plt
# import rasterio.plot as rplt

#           Import Data
S1A_20200218_VV = rasterio.open("...")
S1A_20210619_VV = "..."
S1A_20211022_VV = "..."
aoi = gpd.read_file("...")

#           1. Creating B-Box

# B-Box 1

# B-Box 2

# B-Box 3


#           2. Zonal Statistics /rasterstats/
zona_list_1 = zonal_stats("...shp...", "...tif...", stats="count min median mean max std")

#           3. Calculate Averages
averages = statistics.mean(var1, var2, var3)

#           3.1 Export results
# ??right txt file??
