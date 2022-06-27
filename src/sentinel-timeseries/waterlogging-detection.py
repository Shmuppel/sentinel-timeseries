import os
import geopandas as gpd
from dotenv import load_dotenv

from pyproj import CRS

from api import *
from indices import MNDWI_XU
from rasterstats import zonal_stats
from util import get_polygon_from_geojson
from band import Band


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


def process_sentinel1(api, parcels):
    sentinel1_products = api.get_sentinel1_products(date(2022, 1, 1), date(2022, 1, 7))
    for product in sentinel1_products:
        product.get_bands([Band(mission='Sentinel1', band='VV'), Band(mission='Sentinel1', band='VH')])
        # product['VV'].array
        # product['VH'].array
        breakpoint()


def main():
    load_dotenv()

    study_area = get_polygon_from_geojson('../resources/study_area/Polygon_WGS84.geojson')
    parcels = gpd.read_file('../resources/study_area/AOI_BRP_WGS84.geojson')

    api = SentinelTimeseriesAPI(
        username=os.getenv('COPERNICUS_HUB_USERNAME'),
        password=os.getenv('COPERNICUS_HUB_PASSWORD'),
        aoi=study_area,
        warp=CRS('EPSG:4326'),
        working_directory='../resources/images'
    )
    process_sentinel1(api, parcels)
    #process_sentinel2(api, parcels)


if __name__ == '__main__':
    main()
