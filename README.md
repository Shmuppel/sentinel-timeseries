# Sentinel Timeseries

## About

## Getting Started
```

```

```
COPERNICUS_USERNAME = 'your_username'
COPERNICUS_PASSWORD = 'your_password'
```

## Usage
### Connecting to Copernicus Open Access Hub
sentinelsat

### Retrieving Sentinel Products
aoi
daterange
#### Retrieving Long Term Archival Images

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
From here you can open the files with the library of your choice. Some utility functions are included for processing the images
with numpy (see waterlogging example).

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

### Warping / Changing CRS

