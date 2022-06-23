# Import packages
import os
import numpy as np
from matplotlib import pyplot as plt
from src.data_exploration.sentinel_1.s1_rgb_edited import get_s1_rgb
from rasterio.plot import show
import geopandas as gpd
from rasterstats import zonal_stats
#os.chdir('C:\\Projects\\pooling-detection')

# Get different files from API
# Put in dictionary
def zip_dict():
    zip1 = r"E:\ACt\S1A_IW_GRDH_1SDV_20210818T171714_20210818T171739_039287_04A39F_A07A.zip"
    zip2 = r'E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip'
    zip3 = r'E:\ACt\S1B_IW_GRDH_1SDV_20210824T171645_20210824T171710_028391_036337_CA81.zip'
    S1_dict = {1: zip1, 2: zip2, 3: zip3}
    return S1_dict


# Make RGB stacks of them using the main in S1_RGB -> s1_rgb_edited.py
def RGB_dict(input_dict):
    rgb_dictionary = {}
    for index, value in enumerate(input_dict.values()):
        rgb_s1 = get_s1_rgb(value)
        rgb_dictionary['RGB_' + str(index)] = rgb_s1
    print(rgb_dictionary)
    return rgb_dictionary


#Plot the individual images
#for i in range(len(array_stack)):
 #   #show(array_stack[i])
 #   plt.figure(i+1)
 #   plt.title(i)
 #   plt.show()
 #   show(array_stack[i])


#### Zonal statistics per parcel
def get_zonalstats_s1(rgbs, parcels):
    all_stats = []
    for key, value in rgbs.items():
        raster = np.load(value[0])
        for element in raster:
            all_stats.append(zonal_stats(parcels,
                                     element,
                                     stats=['count', 'min', 'median', 'mean', 'max', 'std'],
                                     affine=value[1],
                                     nodata=-999.))
    print('Zonal statistics are calculated')
    return all_stats
#Returns statistics for all parcels on three dates for all three the bands. So no. of parcels * 9


def s1_stat(all_statistics, parcels, stat_type):
    breakpoint()
    for list in all_statistics:
        for element in list:
            stat = element.get(stat_type)
            parcels[stat]
    return parcels

    #stat_type = [stats[stat_type] for stats in all_statistics]
    #counts = [stats['count'] for stats in zonal_statistics]
    #parcels[stat_type] = stat_type
    #return parcels



#count_counts = number of pixels per parcel that are in between the thresholds

#stats = stats per parcel, output of get_zonalstats
def plot_S1_stats(parcels, stat, stats_dataset):
    fig, ax = plt.subplots(figsize=(12, 8))
    parcels.plot(column=stat, legend=True, cmap='Spectral', ax=ax)
    ax.set_title(stats_dataset + stat, fontsize=30)
    plt.show()



def main_tsa():
    #Get zipfiles with S1 raw tiff files
    S1_dict = zip_dict()

    #Create dictionary with RGB stacks for the different zip files
    rgbs = RGB_dict(S1_dict)

    #Read in parcels
    parcels = gpd.read_file("resources/study_area/AOI_BRP_WGS84.geojson")

    #Create bounding box
    #Can be removed later if code works, replace by 'parcels'
    bbox = parcels.loc[parcels['OBJECTID_1'].isin([1079, 562, 121, 1037]), :]

    #Get zonal statistics (count, min, median, mean, max, std) per parcel and per date
    zonal_stats = get_zonalstats_s1(rgbs, bbox)

    #The following statistics can be plotted:
    #'count', 'min', 'median', 'mean', 'max', 'std'
    #Get the maximum and plot it
    breakpoint()
    maximum = s1_stat(zonal_stats, bbox, 'max')
    plot_S1_stats(bbox, maximum, zonal_stats)

    return zonal_stats

if __name__ == '__main__':
    main_tsa()
