
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
# import json
#
# js = open('resources/study_area/BRP_AOI_RDNew.geojson', 'r').read()
# gj = json.loads(js)
#
# output = { "type": "FeatureCollection", "features": [] }
#
# for feature in gj['features']:
#     if (feature['geometry'] is not None) and (feature['geometry']['type'] == 'MultiPolygon'):
#         for poly in feature['geometry']['coordinates']:
#             xfeature = { "type": "Feature", "properties": {}, "geometry": { "type": "Polygon" } }
#             xfeature['geometry']['coordinates'] = poly
#             output['features'].append(xfeature)
#
# open('polygons.geojson', 'w').write(json.dumps(output))

#breakpoint()
#load parcels
parcelpath = "resources/study_area/BRP_AOI_RDNew.geojson"
parcels = get_study_area(parcelpath)
#gpd.datasets.available
#parcelsall = gpd.read_file(parcelpath)
#parcels = pd.DataFrame(parcelsall)


# parcelpath = 'resources/study_area/Polygon.geojson'
# parcels = get_study_area(parcelpath)

#polygon into geojson
transformer = pyproj.Transformer.from_crs(
    pyproj.CRS('EPSG:28992'),  # Assuming the study / crop area is in RD New
    pyproj.CRS('EPSG:32631'),  # The CRS as specified in the image
    always_xy=True).transform

breakpoint()

#load indice maps
ndwi_gao, ndwi_mcfeeters, mndwi_xu, geometry_transform = calculate_indices()

breakpoint()
#do some calculations with zonal_stats
masked_band = np.ma.array(ndwi_gao, mask=(ndwi_gao.mask), dtype=np.float32, affine = geometry_transform, fill_value=-999.)
masked_filled = masked_band.filled()


parcel_json = json.dumps(shapely.geometry.mapping(parcels))

breakpoint()
#zonal_stats(parcel_json)
gao_stats = zonal_stats(parcel_json, masked_filled, nodata = -999.)

show(ndwi_gao, title='NDWI GAO', cmap='gist_ncar')
#show(parcels, title='NDWI GAO', cmap='gist_ncar')

#plt.show(parcels)

#xu_stats = zonal_stats(parcels, mndwi_xu, affine = geometry_transform)

#mcfeeters_stats = zonal_stats(parcels, ndwi_mcfeeters, affine = geometry_transform)