import os
from dotenv import load_dotenv
import shutil

from pyproj import CRS

from api import *
from indices import NDWI_GAO
from util import get_polygon_from_geojson


def cleanup(path):
    shutil.rmtree(path)
    os.mkdir(path)
    os.mkdir(path + '/warped')


def main():
    # args = parse_command_line()
    #cleanup('../resources/images/sentinel2')
    load_dotenv()
    study_area = get_polygon_from_geojson('../resources/study_area/Polygon_WGS84.geojson')
    api = NearRealtimeAPI(
        username=os.getenv('COPERNICUS_HUB_USERNAME'),
        password=os.getenv('COPERNICUS_HUB_PASSWORD'),
        footprint=study_area,
        warp=CRS('EPSG:4326'),
        working_directory='../resources/images'
    )
    # sentinel1_products = api.get_sentinel1_products(date(2022, 1, 1), date(2022, 1, 7))
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 2, 27))
    for product in sentinel2_products:
        ndwi_gao = NDWI_GAO(product)
        breakpoint()


if __name__ == '__main__':
    main()
