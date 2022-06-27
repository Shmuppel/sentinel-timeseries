from datetime import date
from indices import MNDWI_XU
from rasterstats import zonal_stats


def process_sentinel2(api, parcels):
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 2, 27))
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
            stats=['count', 'max', 'mean', 'percentile_95', 'nodata']
        )
        breakpoint()
