#A code that calculates the Indices based on downloaded Sentinel 2 data

#Import stuff
#from osgeo import gdal
#import os
#import numpy
import rasterio
from rasterio.plot import show
from rasterio.enums import Resampling
#from rasterio.features import features
#from matplotlib import pyplot

#A function that has two bands as input and calculates the indices.

def calIndices (band1, band2):
  return (band1 - band2) / (band1 + band2)
  # up = numpy.subtract(band1, band2)
  # down = numpy.sum(band1, band2)
  # NDMI = numpy.devide(up, down)
  #
  # return NDMI

#This function reprojects image data, here it is used to reproject the swir to the other resolutions


def get_image_data(image_path, resample=None):
  with rasterio.open(image_path) as ds:
    epsg = ds.crs.to_epsg() if ds.crs else 4326

    # zone_polygon = shapely.geometry.shape(json.loads(zone_transformed.geojson))
    # Crop raster -- get bounding window of shape(s) in raster.
    # window = rasterio.features.geometry_window(ds, [])
    # window_transform = ds.window_transform(window)
    # Either set a new shape for the data or use the window's shape.
    # Limit raster to window, apply resampling if desired.
    shape = (resample[0], resample[1]) if isinstance(resample, tuple) else ds.shape

    data = ds.read(
      out_shape=shape,
      #window=window,
      resampling=Resampling.cubic
    )

    return data[0]

#Load the sentinel 2 data from data paths,
# Can still be upgraded to included other locations

#load green band
homegreen="Data/S2A_MSIL1C_20210823T105031_N0301_R051_T31UFU_20210823T144408.SAFE/GRANULE/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B03.jp2"
greenarray = get_image_data(homegreen,)
#greenarray = numpy.array(green.read())

#load NIR Band
homenir="Data/S2A_MSIL1C_20210823T105031_N0301_R051_T31UFU_20210823T144408.SAFE/GRANULE/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B08.jp2"
nirarray = get_image_data(homenir,)
#nirarray = numpy.array(nir.read())

#load SWIR Data
homeswir="Data/S2A_MSIL1C_20210823T105031_N0301_R051_T31UFU_20210823T144408.SAFE/GRANULE/L1C_T31UFU_A032223_20210823T105351/IMG_DATA/T31UFU_20210823T105031_B11.jp2"
swirarray = get_image_data(homeswir, resample=greenarray.shape)
#swirarray = numpy.array(swir.read())


#Calls the finction that calculates the indices.
NDMI_GAO = calIndices(nirarray, swirarray)
ModifiedNDMI_Xu = calIndices(greenarray, swirarray)
NDMI_McFeeters = calIndices(greenarray, nirarray)


#Show indice map
#rasterio.plot.show(NDMI_GAO)

# #print(green.meta)
show(NDMI_GAO, title = 'GAO NDWI', cmap = 'gist_ncar')
# #print(nir.meta)
show(ModifiedNDMI_Xu, title = 'ModifiedMDWI', cmap = 'gist_ncar')
# #print(swir.meta)
show(NDMI_McFeeters, title = 'MDWI McFeeters', cmap = 'gist_ncar')