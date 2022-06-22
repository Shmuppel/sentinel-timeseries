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


#do some calculations with zonal_stats
masked_band = np.ma.array(ndwi_gao, mask=(ndwi_gao.mask), dtype=np.float32, fill_value=-999)
masked_filled = masked_band.filled()

#parcel_json = json.dumps(shapely.geometry.mapping(new_parcels))
#zonal_stats(parcel_json)
#['{"type": "Polygon", "coordinates": [[[684827.2392268141, 5884044.476651217], [684829.3855335615, 5884042.766186684], ...]

gao_stats = zonal_stats([shapely.geometry.mapping(parcel) for parcel in new_parcels], masked_filled, affine = geometry_transform, nodata = -999)

#add colum to dataframe with the count data
panda_parcel = gpd.GeoSeries(new_parcels)

counts = [stats['count'] for stats in gao_stats]

panda_parcel['count'] = counts




#plot count data in color from data frame

print(gao_stats)
#show(ndwi_mcfeeters, title='NDWI mcfeeters', cmap='gist_ncar')

#geopandas dataframe get count, min, max, mean

counts = [stats['count'] for stats in gao_stats]
geoparcels['counts'] = counts


geoparcels.plot(column='counts', legend=True)
plt.show()
