"""
Title: Clip to area extend and select partials
Author: Sotiris Kechagias (MasterHydro) et al
Date: 2022/06/14 (Tue)
"""

# Import Packages
import os
import rasterio
import numpy as np
from rasterio import plot
from rasterio.plot import show

# Import Data
# Raster / Images
# Create a data directory within the directory where this script is run if it does not exist yet and store file
if not os.path.exists('Data'): os.makedirs('Data')
# band1 = rasterio.open("./Data/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B01.jp2")


# Shapefiles
