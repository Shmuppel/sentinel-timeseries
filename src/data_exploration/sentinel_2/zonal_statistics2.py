#load libraries
from rasterstats import zonal_stats
from rasterio.plot import show
from src.util import *
from src.data_exploration.sentinel_2.s2_indices import calculate_indices
import matplotlib.pyplot as plt
import shapely
import geopandas as gpd
import pandas as pd


#import shapefile

#load parcels
parcelpath = "resources/study_area/BRP_AOI_RDNew.geojson"
#parcelsall = get_study_area(parcelpath)
parcelsall = get_parcels(parcelpath)
geoparcels = gpd.read_file(parcelpath)
geomparcels = geoparcels['geometry']
# Polygon into geojson
transformer = pyproj.Transformer.from_crs(
    pyproj.CRS('EPSG:28992'),  # Assuming the study / crop area is in RD New
    pyproj.CRS('EPSG:32631'),  # The CRS as specified in the image
    always_xy=True).transform
#parcels = transform(transformer, parcelsall)

new_parcels = [transform(transformer, shape(parcel['geometry'])) for parcel in parcelsall['features']]


#load indice maps
ndwi_gao, ndwi_mcfeeters, mndwi_xu, geometry_transform = calculate_indices()

###ZONAL STATS
#Goastats
masked_band_gao = np.ma.array(ndwi_gao, mask=(ndwi_gao.mask), dtype=np.float32, fill_value=-999)
masked_filled_gao = masked_band_gao.filled()

#Goa zonal stats
gao_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled_gao, affine = geometry_transform, nodata = -999, stats=['count', 'max', 'mean','percentile_95'])
###END GAO

#mndwi_Xu calculations
masked_band_xu = np.ma.array(mndwi_xu, mask=(mndwi_xu.mask), dtype=np.float32, fill_value=-999)
masked_filled_xu = masked_band_xu.filled()

#MNDWI zonalstats
mndwi_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled_xu, affine = geometry_transform, nodata = -999, stats=['count', 'max', 'mean','percentile_95'])
###END MNDWI

#ndwi_mcfeeters calculations
masked_band_mcfeeters = np.ma.array(ndwi_mcfeeters, mask=(ndwi_mcfeeters.mask), dtype=np.float32, fill_value=-999)
masked_filled_mcfeeters = masked_band_mcfeeters.filled()

#ndwi zonalstats
mcfeeters_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled_mcfeeters, affine = geometry_transform, nodata = -999, stats=['count', 'max', 'mean','percentile_95'])
### END MCFEETERS





## GAO Stats adding
counts = [stats['count'] for stats in gao_stats]
geoparcels['counts_gao'] = counts

mean = [stats['mean'] for stats in gao_stats]
geoparcels['mean_gao'] = mean

rmax = [stats['max'] for stats in gao_stats]
geoparcels['max_gao'] = rmax

percentile = [stats['percentile_95'] for stats in gao_stats]
geoparcels['percentile_gao'] = percentile

#MNDWI Stats adding
counts = [stats['count'] for stats in mndwi_stats]
geoparcels['counts_mndwi'] = counts

mean = [stats['mean'] for stats in mndwi_stats]
geoparcels['mean_mndwi'] = mean

rmax = [stats['max'] for stats in mndwi_stats]
geoparcels['max_mndwi'] = rmax

percentile = [stats['percentile_95'] for stats in mndwi_stats]
geoparcels['percentile_mndwi'] = percentile


#mcfeeters Stats adding
counts = [stats['count'] for stats in mcfeeters_stats]
geoparcels['counts_mcfeeters'] = counts

mean = [stats['mean'] for stats in mcfeeters_stats]
geoparcels['mean_mcfeeters'] = mean

rmax = [stats['max'] for stats in mcfeeters_stats]
geoparcels['max_mcfeeters'] = rmax

percentile = [stats['percentile_95'] for stats in mcfeeters_stats]
geoparcels['percentile_mcfeeters'] = percentile

#PLOT

def plot_all_indices(data, count, mean, max, percentile, name):
    fig, ax = plt.subplots(figsize=(12, 8))

    data.plot(column=count, legend=True, cmap='Spectral',ax=ax )
    ax.set_title(name + count, fontsize=30)
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
    ax.set_title(name + percentile, fontsize=30)
    plt.show()

#gao plotting
plot_all_indices(geoparcels, 'counts_gao', 'mean_gao', 'max_gao', 'percentile_gao', 'NDWI ')

#mndwi plotting
plot_all_indices(geoparcels, 'counts_mndwi', 'mean_mndwi', 'max_mndwi', 'percentile_mndwi', 'MNDWI ')

#mcfeeters plotting
plot_all_indices(geoparcels, 'counts_mcfeeters', 'mean_mcfeeters', 'max_mcfeeters', 'percentile_mcfeeters', 'Mc Feeters ')




#hotspot algorihtm
amount_of_images = 4

#for images in amount_of_images:

#parcel_json = json.dumps(shapely.geometry.mapping(new_parcels))
#zonal_stats(parcel_json)
#['{"type": "Polygon", "coordinates": [[[684827.2392268141, 5884044.476651217], [684829.3855335615, 5884042.766186684], ...]


#plot count data in color from data frame

# print(gao_stats)
#show(ndwi_mcfeeters, title='NDWI mcfeeters', cmap='gist_ncar')

#geopandas dataframe get count, min, max, mean
