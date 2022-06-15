#### Import Packages ####
from zipfile import ZipFile
import gdal
import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
from matplotlib import pyplot as plt


#### Links to Sentinel 1 images ####
#Link to Sentinel 1 Image 23-08-2021 from SentinelHub
# s3://sentinel-s1-l1c/GRD/2021/8/23/IW/DV/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894/

# I downloaded one S1 tile from https://search.asf.alaska.edu/#/?zoom=7.252&center=9.200,52.727&polygon=POLYGON((5.5751%2052.986,5.8622%2052.986,5.8622%2053.1695,5.5751%2053.1695,5.5751%2052.986))&start=2021-08-21T22:00:00Z&end=2021-08-24T21:59:59Z&flightDirs=Ascending&resultsLoaded=true&granule=S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894-GRD_HD
# https://appdividend.com/2022/01/19/python-unzip/#:~:text=To%20unzip%20a%20file%20in,inbuilt%20python%20module%20called%20zipfile.


#### Unzip tiff files ####
with ZipFile('E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip', 'r') as zipObj:
    listOfFileNames = zipObj.namelist()
    for fileName in listOfFileNames:
        if fileName.endswith('.tiff'):
            # Extract a single file from zip
            zipObj.extract(fileName, 'temp_tiff')
            print('All the TIFF files are extracted in temp_tiff')


#### Open TIFF files using gdal ####
dirname = 'temp_tiff/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.SAFE/measurement'
vh_name = 's1a-iw-grd-vh-20210823t172521-20210823t172546-039360-04a618-002.tiff'
vv_name = 's1a-iw-grd-vv-20210823t172521-20210823t172546-039360-04a618-001.tiff'
vh_backscatter = gdal.Open(os.path.join(dirname, vh_name))
vv_backscatter = gdal.Open(os.path.join(dirname, vv_name))
data_vh = vh_backscatter.ReadAsArray()
data_vv = vv_backscatter.ReadAsArray()


#### Convert from backscatter to dB ####
# Convert to dB
vv_dB = np.log10(data_vv, out=np.zeros_like(data_vv, dtype='float32'), where=(data_vv!=0))
vh_dB = np.log10(data_vh, out=np.zeros_like(data_vh, dtype='float32'), where=(data_vh!=0))
vh_dB = vh_dB.astype('float16')
vv_dB = vv_dB.astype('float16')

#Check if it does something (yes!)
vh_dB_max = np.max(vh_dB)
vh_dB_min = np.min(vh_dB)
vv_dB_max = np.max(vv_dB)
vv_dB_min = np.min(vv_dB)


#### Calculate vv-vh ratio ####
vv_vh_ratio = vv_dB - vh_dB
plt.imshow(vv_vh_ratio)
plt.show()
#Check if it works
vv_vh_ratio_min = np.min(vv_vh_ratio)
vv_vh_ratio_max = np.max(vv_vh_ratio)


#### Load AOI ####
AOI_GDF = gpd.read_file('resources/study_area/Polygon_WGS84.geojson')
crs = 4326
AOI_GDF = AOI_GDF.to_crs(epsg=crs)
AOI_GDF.plot(aspect=1)


#### Create stack of vv, vh, vv/vh ####
S1_RGB = np.dstack((vv_dB, vh_dB, vv_vh_ratio))

#Conversion factor
max_value_vv_vh_ratio = np.max((vv_dB_max, vh_dB_max, vv_vh_ratio_max))
cf = max_value_vv_vh_ratio / 256
r = vv_dB * cf
print('min r', np.min(r), 'max r', np.max(r))
g = vh_dB * cf
print('min g', np.min(g), 'max g', np.max(g))
b = vv_vh_ratio * cf
print('min b', np.min(b), 'max b', np.max(b))

#### Display as RGB image ####
from PIL import Image
rgbArray = np.zeros((16683,26323,3), 'float16')
rgbArray[..., 0] = r*256
rgbArray[..., 1] = g*256
rgbArray[..., 2] = b*256
img = Image.fromarray(rgbArray)
img.save('temp_tiff/RGB.jpeg')


#### Crop RGB stack ####
def get_image_data(image_path, zone, resample=None):

    with rasterio.open(image_path) as ds:
        epsg = ds.crs.to_epsg()
        # Crop raster -- get bounding window of shape(s) in raster.
        window = rasterio.features.geometry_window(ds, [zone])
        window_transform = ds.window_transform(window)
        # Either set a new shape for the data or use the window's shape.
        shape = (resample[0], resample[1]) if isinstance(resample, tuple) else (window.height, window.width)
        # Limit raster to window, apply resampling if desired.
        data = ds.read(
            out_shape=shape,
            window=window,
            resampling=Resampling.cubic
        )
        transform = window_transform * window_transform.scale((window.width / data.shape[-1]), (window.height / data.shape[-2]))
        # Apply geometry mask.
        geometry_mask = rasterio.features.geometry_mask([zone_polygon], data[0].shape, transform)
        band_masked = np.ma.array(data[0], mask=geometry_mask, dtype=np.int16, fill_value=0)

        return band_masked



AOI_WGS84 = gpd.read_file('resources/study_area/Polygon_WGS84.geojson')
print("AOI_WGS84", AOI_WGS84.crs)
geoms = AOI_WGS84.geometry.values
geometry = geoms[0]
geoms = [mapping(geoms[0])]
