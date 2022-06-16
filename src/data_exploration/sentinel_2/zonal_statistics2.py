from rasterstats import zonal_stats
from src.util import *
from src.data_exploration.sentinel_2.s2_indices import main

parcel_path = 'resources/study_area/AOI_BRP_WGS84.geojson'
parcels = get_study_area(parcel_path)

# polygon_path = 'resources/study_area/Polygon.geojson'
# aoi_polygon = get_study_area(polygon_path)

ndwi_gao, ndwi_mcfeeters, mndwi_xu = main()

stats1 = zonal_stats(parcels, ndwi_gao, stats='mean')

stats2 = zonal_stats()

stats3 = zonal_stats()
