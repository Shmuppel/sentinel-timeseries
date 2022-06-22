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


#do some calculations with zonal_stats for NDWI Gao index
masked_band = np.ma.array(ndwi_gao, mask=(ndwi_gao.mask), dtype=np.float32, fill_value=-999)
masked_filled = masked_band.filled()

gao_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled, affine = geometry_transform, nodata = -999, stats='percentile_95')

print(gao_stats)

fig, ax = plt.subplots(figsize = (12, 8))
perc = [stats['percentile_95'] for stats in gao_stats]
geoparcels['gao_percentile_95'] = perc
geoparcels.plot(column='gao_percentile_95',ax=ax, cmap='Spectral', legend=True)
ax.set_title("Gao - percentile_95", fontsize=30)
plt.show()

#do some calculations with zonal_stats for NDWI mcfeeters
masked_band2 = np.ma.array(ndwi_mcfeeters, mask=(ndwi_mcfeeters.mask), dtype=np.float32, fill_value=-999)
masked_filled2 = masked_band.filled()

mcfeeters_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled2, affine = geometry_transform, nodata = -999, stats='percentile_95')

print(mcfeeters_stats)

fig, ax = plt.subplots(figsize = (12, 8))

percmcfeeters = [stats['percentile_95'] for stats in mcfeeters_stats]
geoparcels['feeters_percentile_95'] = percmcfeeters
geoparcels.plot(column='feeters_percentile_95',ax=ax, cmap='Spectral', legend=True)
ax.set_title("McFeeters - percentile_95", fontsize=30)
plt.show()
#do some calculations with zonal_stats for NDWI mndwi Xu
masked_band3 = np.ma.array(mndwi_xu, mask=(mndwi_xu.mask), dtype=np.float32, fill_value=-999)
masked_filled3 = masked_band3.filled()

mndwi_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled3, affine = geometry_transform, nodata = -999, stats='percentile_95')

print(mndwi_stats)

fig, ax = plt.subplots(figsize = (12, 8))

perc = [stats['percentile_95'] for stats in mndwi_stats]
geoparcels['mndwi_percentile_95'] = perc
geoparcels.plot(column='mndwi_percentile_95',ax=ax, cmap='Spectral', legend=True)
ax.set_title("MNDWI, Xu - percentile_95", fontsize=30)
plt.show()
#show(ndwi_mcfeeters, title='NDWI mcfeeters', cmap='gist_ncar')

#geopandas dataframe get count, min, max, mean
'''
perc = [stats['percentile_95'] for stats in gao_stats]
geoparcels['percentile_95'] = perc
geoparcels.plot(column='percentile_95', cmap='Spectral', legend=True)
plt.show()


counts = [stats['count'] for stats in gao_stats]
geoparcels['counts'] = counts
geoparcels.plot(column='counts',cmap='prism', legend=True)
plt.show()

max = [stats['max'] for stats in gao_stats]
geoparcels['max'] = max
geoparcels.plot(column='max',cmap='hot', legend=True)
plt.show()

mean = [stats['mean'] for stats in gao_stats]
geoparcels['mean'] = mean
geoparcels.plot(column='mean', cmap='hot', legend=True)
plt.show()
'''