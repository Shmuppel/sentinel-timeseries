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
```python
# Sentinel 1
VV = product['VV']
VV, VH = product['VV', 'VH']

# Sentinel 2
band3 = product['B03']
band3, band8a = product['B03', 'B8a']
band3 = product.get_band('B03')
```  

### Ad-hoc Requesting

### Handling temporary data
`product.remove()`
```python
# Automatically calls product.remove() on exit
with product:
    ...
```

### Warping / Changing CRS

