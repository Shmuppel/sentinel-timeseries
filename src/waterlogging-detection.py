import os
from dotenv import load_dotenv

from pyproj import CRS

from api import *
from indices import NDWI_GAO, NDWI_MCFEETER, MNDWI_XU
from util import get_polygon_from_geojson


def main():
    load_dotenv()

    study_area = get_polygon_from_geojson('../resources/study_area/Polygon_WGS84.geojson')

    api = SentinelTimeseriesAPI(
        username=os.getenv('COPERNICUS_HUB_USERNAME'),
        password=os.getenv('COPERNICUS_HUB_PASSWORD'),
        aoi=study_area,
        warp=CRS('EPSG:4326'),
        working_directory='../resources/images'
    )

    # sentinel1_products = api.get_sentinel1_products(date(2022, 1, 1), date(2022, 1, 7))
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 2, 27))

    for product in sentinel2_products:
        ndwi_gao = NDWI_GAO(product)
        ndwi_mcfeeter = NDWI_MCFEETER(product)
        mndwi_xu = MNDWI_XU(product)
        breakpoint()


if __name__ == '__main__':
    main()
