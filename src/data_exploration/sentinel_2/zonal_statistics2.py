#load libraries
from rasterstats import zonal_stats
from src.util import *
from src.data_exploration.sentinel_2.s2_indices import calculate_indices
import matplotlib.pyplot as plt
import shapely
import geopandas as gpd


#Load parcel map
new_parcels, geoparcels = load_parcels("resources/study_area/BRP_AOI_RDNew.geojson")

#load indice maps
ndwi_gao, ndwi_mcfeeters, mndwi_xu, geometry_transform = calculate_indices()


###ZONAL STATS
#Gao
gao_stats = zonals(ndwi_gao, geometry_transform, new_parcels)

#Mndwi
mndwi_stats = zonals(mndwi_xu, geometry_transform, new_parcels)

#Ndwi Mcfeeters
mcfeeters_stats = zonals(ndwi_mcfeeters, geometry_transform, new_parcels)


# Gao stats to Geodataframe
stats_to_gdf(gao_stats,geoparcels,"gao")

# mcfeeters stats to Geodataframe
stats_to_gdf(mcfeeters_stats, geoparcels,"mcfeeters")

# mndwi stats to Geodataframe
stats_to_gdf(mndwi_stats, geoparcels,"mndwi")


#gao plotting
plot_all_indices(geoparcels, 'counts_gao', 'mean_gao', 'max_gao', 'percentile_gao', 'NDWI ')

#mndwi plotting
plot_all_indices(geoparcels, 'counts_mndwi', 'mean_mndwi', 'max_mndwi', 'percentile_mndwi', 'MNDWI ')

#mcfeeters plotting
plot_all_indices(geoparcels, 'counts_mcfeeters', 'mean_mcfeeters', 'max_mcfeeters', 'percentile_mcfeeters', 'Mc Feeters ')




#hotspot algorihtm
amount_of_images = 4

