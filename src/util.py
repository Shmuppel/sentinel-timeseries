import json
import numpy as np
import pyproj
import rasterio
import rasterio.features
from rasterio.enums import Resampling
from shapely.geometry import shape, box
from shapely.ops import transform
import matplotlib.pyplot as plt
import shapely
import geopandas as gpd
from rasterstats import zonal_stats

def calculate_normalized_index(band1, band2):
    """ Returns a normalized index from two bands. """
    return (band1 - band2) / (band1 + band2)


def get_study_area(file_path: str):
    """ Returns the study area as shapely Polygon. """
    with open(file_path, 'r') as f:
        aoi_json = json.load(f)['features']
        aoi_shape = shape(aoi_json[0]["geometry"])
    return aoi_shape


def get_parcels(file_path: str):
    with open(file_path, 'r') as f:
        parcel_json = json.load(f)
    return parcel_json


def get_image_data(
        image_path: str,
        crop_shape,
        resample=None
):
    """
  image_path: Opens a image using rasterIO given an image path.
  zone: Clips the image to the zone, this should be some kind of Polygon.
  resample: Resamples the image to given dimensions.
  """
    with rasterio.open(image_path) as ds:
        assert ds.crs  # Raise error if image does not have CRS
        print(f'Satellite image CRS: {ds.crs.to_epsg()}')
        transformer = pyproj.Transformer.from_crs(
            pyproj.CRS('EPSG:28992'),  # Assuming the study / crop area is in RD New
            pyproj.CRS(f'EPSG:{ds.crs.to_epsg()}'),   # The CRS as specified in the image
            always_xy=True).transform
        crop_shape = transform(transformer, crop_shape)
        bounding_box = box(*crop_shape.bounds)

        # Crop raster -- get bounding window of shape(s) in raster.
        window = rasterio.features.geometry_window(ds, [bounding_box])
        window_transform = ds.window_transform(window)

        # Either set a new shape for the data or use the window's shape.
        out_shape = (resample[0], resample[1]) if isinstance(resample, tuple) else (window.height, window.width)

        # Limit raster to window, apply resampling if desired.
        data = ds.read(
            out_shape=out_shape,
            window=window,
            resampling=Resampling.cubic
        )
        # We have to transform the window (our cropped view) to a resampled view if we resampled.
        geometry_transform = window_transform * window_transform.scale((window.width / data.shape[-1]),
                                                                       (window.height / data.shape[-2]))
        # Apply geometry mask.
        geometry_mask = rasterio.features.geometry_mask([crop_shape], data[0].shape, geometry_transform)
        band_masked = np.ma.array(data[0], mask=geometry_mask, dtype=np.int16, fill_value=0)

        return band_masked, geometry_transform


def stats_to_gdf(index_stat,geodataframe,indexname):
    # Adding statistical data: count, mean, max and percentile, to a geodataframe
    # count
    counts = [stats['count'] for stats in index_stat]
    geodataframe['counts_'+ indexname] = counts
    # mean
    mean = [stats['mean'] for stats in index_stat]
    geodataframe['mean_' + indexname] = mean
    # max
    rmax = [stats['max'] for stats in index_stat]
    geodataframe['max_' + indexname] = rmax
    # percentile
    percentile = [stats['percentile_95'] for stats in index_stat]
    geodataframe['percentile_' + indexname] = percentile

    return geodataframe

#function that loads the file of the idices based on a given path
def load_parcels (file_path):
    #create parcelpath

    parcelpath = file_path
    parcelsall = get_parcels(parcelpath)
    geoparcels = gpd.read_file(parcelpath)

    # Polygon into geojson
    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS('EPSG:28992'),  # Assuming the study / crop area is in RD New
        pyproj.CRS('EPSG:32631'),  # The CRS as specified in the image
        always_xy=True).transform

    new_parcels = [transform(transformer, shape(parcel['geometry'])) for parcel in parcelsall['features']]

    return new_parcels, geoparcels

#Function that calculates the zonalstatistics of the indices
def zonals (indice, geometry_transform, new_parcels):
    #Make an array of the indices

    masked_band = np.ma.array(indice, mask=(indice.mask), dtype=np.float32, fill_value=-999)
    masked_filled = masked_band.filled()

    #Zonal stats of the indices
    stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled,
                            affine=geometry_transform, nodata=-999, stats=['count', 'max', 'mean', 'percentile_95'])
    return stats

#A Function that plots the zonal stats
def plot_all_indices(data, count, mean, max, percentile, name):
    fig, ax = plt.subplots(figsize=(12, 8))
    x = name + count
    data.plot(column=count, legend=True, cmap='Spectral',ax=ax )
    ax.set_title(x, fontsize=30)
    plt.show()

    fig, ax = plt.subplots(figsize=(12, 8))
    data.plot(column=mean, legend=True, cmap='Spectral',ax=ax)
    ax.set_title(name + mean, fontsize=30)
    plt.show()

    fig, ax = plt.subplots(figsize=(12, 8))
    data.plot(column=max, legend=True, cmap='Spectral',ax=ax)
    ax.set_title(name + max, fontsize=30)
    plt.show()

    fig, ax = plt.subplots(figsize=(12, 8))
    data.plot(column=percentile, legend=True, cmap='Spectral',ax=ax)
    ax.set_title(name+ percentile, fontsize=30)
    plt.show()

def plot1_indices(data, to_plot, name):
    fig, ax = plt.subplots(figsize=(12, 8))

    data.plot(column=to_plot, legend=True, cmap='Spectral',ax=ax )
    ax.set_title(name + to_plot, fontsize=30)
    plt.show()