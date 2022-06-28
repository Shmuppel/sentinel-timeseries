from datetime import date

import matplotlib.pyplot as plt

from rasterstats import zonal_stats
from util.arrays import get_bands_as_arrays, mask_clouds_and_snow


def process_sentinel2(api, parcels):
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 5, 1))
    parcels = parcels.assign(stat_count=0, stat_percentile95=0)

    for product in sentinel2_products:
        bands = product['B03', 'B11', 'CLD', 'SNW']
        band_arrays, affine_transform = get_bands_as_arrays(bands, api.aoi)
        band3, band11, cld, snw = band_arrays['B03'], band_arrays['B11'], band_arrays['CLD'], band_arrays['SNW']

        # Mask clouds and snow from band arrays
        band3_array = mask_clouds_and_snow(band3, cld, snw)
        band11_array = mask_clouds_and_snow(band11, cld, snw)

        # Calculate indice
        mndwi_xu = (band3_array - band11_array) / (band3_array + band11_array)

        # Calculate zonal statistics
        print(f"{product.product_id}: Calculating zonal statistics...")
        stats = zonal_stats(
            parcels,
            mndwi_xu.filled(),
            affine=affine_transform,
            nodata=-999,
            stats=['count', 'percentile_95']
        )

        # Calculate a running sum of statistics
        stat_count, stat_percentile95 = [], []
        # if there are no pixels we replace the statistics with 0
        # this should only be done, because we are summing statistics over multiple images
        for stat in stats:
            stat_count.append(stat['count'])
            stat_percentile95.append(stat['percentile_95'] if stat['percentile_95'] else 0)
        parcels['stat_count'] += stat_count
        parcels['stat_percentile95'] += stat_percentile95

    # Average the percentiles over the amount of hotspots
    parcels['stat_percentile95'] = parcels['stat_percentile95'] / len(sentinel2_products)

    # Plot percentiles per parcel
    fig, ax = plt.subplots(figsize=(12, 8))
    parcels.plot(column='stat_percentile95', legend=True, cmap='Spectral', ax=ax)
    plt.show()
