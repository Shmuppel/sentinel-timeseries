#Link to Sentinel 1 Image 23-08-2021 from SentinelHub
# s3://sentinel-s1-l1c/GRD/2021/8/23/IW/DV/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894/

# I downloaded one S1 tile from https://search.asf.alaska.edu/#/?zoom=7.252&center=9.200,52.727&polygon=POLYGON((5.5751%2052.986,5.8622%2052.986,5.8622%2053.1695,5.5751%2053.1695,5.5751%2052.986))&start=2021-08-21T22:00:00Z&end=2021-08-24T21:59:59Z&flightDirs=Ascending&resultsLoaded=true&granule=S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894-GRD_HD
# https://appdividend.com/2022/01/19/python-unzip/#:~:text=To%20unzip%20a%20file%20in,inbuilt%20python%20module%20called%20zipfile.
from zipfile import ZipFile
with ZipFile('E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip', 'r') as zipObj:
    listOfFileNames = zipObj.namelist()
    for fileName in listOfFileNames:
        if fileName.endswith('.tiff'):
            # Extract a single file from zip
            zipObj.extract(fileName, 'temp_tiff')
            print('All the TIFF files are extracted in temp_tiff')

##Open TIFF files using gdal
import gdal
import os
import numpy as np
dirname = 'temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement'
vh_name = 's1a-iw-grd-vh-20210823t172521-20210823t172546-039360-04a618-002.tiff'
vv_name = 's1a-iw-grd-vv-20210823t172521-20210823t172546-039360-04a618-001.tiff'
vh_backscatter = gdal.Open(os.path.join(dirname, vh_name))
vv_backscatter = gdal.Open(os.path.join(dirname, vv_name))
data_vh = vh_backscatter.ReadAsArray()
data_vv = vv_backscatter.ReadAsArray()

#Replace 0 with nan
#data_vh_nan = np.where(data_vh==0, np.nan, data_vh)
#data_vv_nan = np.where(data_vv==0, np.nan, data_vv)

##Convert from backscatter to dB
import numpy as np
vv_dB = np.log10(data_vv, out=np.zeros_like(data_vv, dtype='float32'), where=(data_vv!=0))
vh_dB = np.log10(data_vh, out=np.zeros_like(data_vh, dtype='float32'), where=(data_vh!=0))
#Check if it does something (yes!)
vh_dB_max = np.max(vh_dB)
vh_dB_min = np.min(vh_dB)
vv_dB_max = np.max(vv_dB)
vv_dB_min = np.min(vv_dB)

## Calculate vv-vh ratio
vv_vh_ratio = vv_dB - vh_dB
vv_vh_ratio_min = np.min(vv_vh_ratio)
vv_vh_ratio_max = np.max(vv_vh_ratio)

#Open area of interest and crop vv and vh images
import geopandas as gpd
AOI_WGS84 = gpd.read_file('resources/study_area/Polygon_WGS84.geojson')




### try with rasterio
#import os
#import rasterio
#from rasterio.plot import show
#dirname = r'temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement'
#vh_name = 's1a-iw-grd-vh-20210823t172521-20210823t172546-039360-04a618-002.tiff'
#fp = os.path.join(dirname, vh_name)
#out_tif = "/measurement/vh_backscatter_masked.tif"

#data = rasterio.open(fp)
#crs = rasterio.crs.CRS({"init": "epsg:4326"})
#data.crs = crs
#show(data)