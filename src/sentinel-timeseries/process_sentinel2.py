from datetime import date
from indices import MNDWI_XU
from rasterstats import zonal_stats
import matplotlib.pyplot as plt

def process_sentinel2(api, parcels):
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 3, 31))
    parcels = parcels.assign(stat_count=0, stat_mean=0, stat_max=0, stat_percentile95=0)
    for product in sentinel2_products:
        # ndwi_gao = NDWI_GAO(product)
        # ndwi_mcfeeter = NDWI_MCFEETER(product)
        mndwi_xu = MNDWI_XU(product)
        affine_transform = mndwi_xu.product['03'].array_affine_transform
        print(f"{product.product_id}: Calculating zonal statistics...")
        stats = zonal_stats(
            parcels,
            mndwi_xu.calculate().filled(),
            affine=affine_transform,
            nodata=-999,
            stats=['count', 'max', 'mean', 'percentile_95', 'nodata'])


        stat_count, stat_mean, stat_max, stat_percentile95 = [], [], [], []
        # if there are no pixels we replace the statistics with 0
        # this should only be done, because we are summing statistics over multiple images
        for stat in stats:
            stat_count.append(stat['count'])
            stat_mean.append(stat['mean'] if stat['mean'] else 0)
            stat_max.append(stat['max'] if stat['max'] else 0)
            stat_percentile95.append(stat['percentile_95'] if stat['percentile_95'] else 0)

        parcels['stat_count'] += stat_count
        parcels['stat_mean'] += stat_mean
        parcels['stat_max'] += stat_max
        parcels['stat_percentile95'] += stat_percentile95

    parcels['stat_percentile95'] = parcels['stat_percentile95'] / len(sentinel2_products)


    fig, ax = plt.subplots(figsize=(12, 8))

    parcels.plot(column='stat_percentile95', legend=True, cmap='Spectral', ax=ax)

    plt.show()