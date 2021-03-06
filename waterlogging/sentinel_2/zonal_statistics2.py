#load libraries
from src.util import *
from data_exploration.sentinel_2.s2_indices import calculate_indices

#Load parcel map
new_parcels, geoparcels = load_parcels(r"C:\Projects\pooling-detection\resources\study_area\BRP_AOI_RDNew.geojson")

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
stats_to_gdf(mndwi_stats, geoparcels,"xu")


#gao plotting
plot_all_indices(geoparcels, 'counts_gao', 'mean_gao', 'max_gao', 'percentile_gao', 'NDWI ')

#mndwi plotting
plot_all_indices(geoparcels, 'counts_xu', 'mean_xu', 'max_xu', 'percentile_xu', 'MNDWI ')

#mcfeeters plotting
plot_all_indices(geoparcels, 'counts_mcfeeters', 'mean_mcfeeters', 'max_mcfeeters', 'percentile_mcfeeters', 'NDWI ')




#hotspot algorihtm
amount_of_images = 4

#calculate the stats for multiple images

#sum all pixel values and divede by the amount of images
#create and extra column that has average and plot that
