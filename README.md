# Sentinel Timeseries

## About
Sentinel timeseries is a package that makes it easier to bulk download and process satellite imagery downloaded from the Copernicus Open Access Hub.
## Getting Started
```
pip install git+https://github.com/Shmuppel/sentinel-timeseries
```
To download imagery from the Copernicus Open Access Hub you will have to provide your username and password. For example in a .env file:
```
#.env
COPERNICUS_USERNAME = 'your_username'
COPERNICUS_PASSWORD = 'your_password'
```

## Usage
### Connecting to Copernicus Open Access Hub
Sentinel timeseries uses the sentinelsat package to download Sentinel products from the Copernicus Open Access Hub. It provides Python object abstractions for interacting with Sentinel products and bands. 

To start interacting with the API first create a `SentinelTimeseriesAPI` object:
```python
api = SentinelTimeseriesAPI(
    username=os.getenv('COPERNICUS_HUB_USERNAME'),
    password=os.getenv('COPERNICUS_HUB_PASSWORD'),
    aoi=your_area_of_interest,
    warp=CRS('EPSG:4326'),
    working_directory='../resources/images'
)
```
The `aoi` argument should be a Shapely Polygon. Any images that overlap this polygon will be retrieved from the API.  
The `warp` argument can be used to warp all images to a different CRS upon downloading.
### Retrieving Sentinel Products
The `get_sentinel1_products()`, and `get_sentinel2_products()` functions can be used to get all products in a date range:
```python
sentinel2_products = api.get_sentinel2_products(
    date(2022, 1, 1), 
    date(2022, 12, 1)
    cloudcover=(0, 5)  # for images with cloudcover 0 - 5%
)
```

#### Retrieving Long Term Archival Images (LTA)
Older products might not be directly accessible from the Copernicus Open Access Hub. In that case the images are stored in long-term-archival, meaning they'll first have to be requested before downloading is possible.
Sentinel timeseries will prompt the user if images should be requested from LTA if it encounters any.  

LTA products can only be requested once every 30mins, and it can take up to 24hours for an LTA image to come online.
Sentinel timeseries will automatically attempt requests, and wait untill all images have come online (though this may take a long time).

### Getting Image Bands from Sentinel Products
A products bands can be accessed through the product.bands property, but initially none of these will be downloaded (see ad-hoc requesting). To get a product's band the following code can be used:
```python
# Sentinel 1
VV = product['VV']
VV, VH = product['VV', 'VH']

# Sentinel 2
band3 = product['B03']
band3, band8a = product['B03', 'B8a']

# You can also call get_band directly for 
# easier programmatic retrieval of bands
band3 = product.get_band('B03')
```
This will return a Band object, which contains metadata and the file path location of the downloaded band (accessible through band.path).
From here you can open the files with the library of your choice. 

### Turning Bands into NumPy arrays
Some utility functions are included for processing the images
with numpy (see waterlogging example).

```python
get_band_as_array(
    image_path: str,
    crop_shape: shapely.geometry.shape,
    resample: tuple[int, int] = None
)
```
Will open an image on the image_path, crop it to a given shapely geometry, and optionally resample the cropped area to a given resolution.

```python
get_bands_as_arrays(
    bands: list[Band], 
    crop: shapely.geometry.shape
)
```
Will automatically open a list of Band objects, resample them to the Band with the highest spatial resolution, crop the band to a given Shapely geometry, and return the result as a dictionary of NumPy arrays.

##### Affine transformations
Because NumPy arrays contain no reference to the coordinates contained in our Satallite imagery an affine transform should be applied if you would like to use them for e.g. zonal statistics.
`get_band_as_array` and `get_bands_as_arrays` both return an affine transform object as a second argument.
```python
band_array, affine_transform = get_band_as_array(product['B04'].path, aoi)
```
#### Ad-hoc Requesting
When requesting a band through `product['your_band']` or `product.get_band('your_band')` sentinel-timeseries checks if the band was not downloaded earlier. If not, a request is made to download that band (and that band only) from the Copernicus Open Access Hub.  

### Handling temporary data
When dealing with large time periods it may be required to remove intermediate products to save disk space. Every Product has a
`product.remove()` function that removes the stored data of that product. To ensure that `product.remove()` is always called you can
use the product as a context manager:
```python
# Automatically calls product.remove() when the code block finishes
with product:
    ...
```


