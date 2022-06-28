from datetime import date

import matplotlib.pyplot as plt
import numpy as np

from rasterstats import zonal_stats
from sentineltimeseries.util.arrays import get_bands_as_arrays, mask_clouds_and_snow
from sentineltimeseries.util.gif import create_gif_from_images


def process_sentinel2(api, parcels):
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 12, 1))
    parcels = parcels.assign(stat_count=0, stat_percentile95=0, temp_count=0, temp_percentile95=0)

    for product in sentinel2_products:
        date_string = product.date.strftime("%Y-%m-%d")
        bands = product['B03', 'B08', 'CLD', 'SNW']
        band_arrays, affine_transform = get_bands_as_arrays(bands, api.aoi)
        band3, band8, cld, snw = band_arrays['B03'], band_arrays['B08'], band_arrays['CLD'], band_arrays['SNW']

        # Mask clouds and snow from band arrays
        band3_array = mask_clouds_and_snow(band3, cld, snw)
        band8_array = mask_clouds_and_snow(band8, cld, snw)

        # Calculate indice
        mndwi_xu = (band3_array - band8_array) / (band3_array + band8_array)

        # Calculate zonal statistics
        print(f"{date_string}: Calculating zonal statistics...")
        stats = zonal_stats(
            parcels,
            mndwi_xu.filled(),
            affine=affine_transform,
            nodata=-999,
            stats=['count', 'percentile_95']
        )

        # Calculate a running sum of statistics
        stat_count, stat_percentile95, temp_percentile95 = [], [], []
        for stat in stats:
            stat_count.append(stat['count'])
            # if there are no pixels we replace the statistics with 0
            # this should only be done, because we are summing statistics over multiple images
            stat_percentile95.append(stat['percentile_95'] if stat['percentile_95'] else 0)
            temp_percentile95.append(stat['percentile_95'] if stat['percentile_95'] else np.nan)

        parcels['temp_percentile95'] = temp_percentile95
        parcels['stat_count'] += stat_count
        parcels['stat_percentile95'] += stat_percentile95

        # Plot percentiles per parcel
        fig, ax = plt.subplots(figsize=(8, 8))
        parcels.plot(
            column='temp_percentile95',
            legend=True,
            cmap='Spectral',
            missing_kwds=dict(color="lightgrey"),
            ax=ax,
            vmin=-0.4,
            vmax=0.1)
        ax.set_title(f'95th Percentile of NDWI McFeeters per Parcel - {date_string}')
        plt.savefig(f'./results/{date_string}')

    # Average the percentiles over the amount of hotspots
    parcels['stat_percentile95'] = parcels['stat_percentile95'] / len(sentinel2_products)
    # Plot average percentiles per parcel
    fig, ax = plt.subplots(figsize=(12, 8))
    parcels.plot(column='stat_percentile95', legend=True, cmap='Spectral', ax=ax)
    plt.show()

    create_gif_from_images('./results', './results/timeseries.gif')
