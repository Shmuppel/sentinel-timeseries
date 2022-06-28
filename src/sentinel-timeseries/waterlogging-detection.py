import os
import geopandas as gpd
from dotenv import load_dotenv

from pyproj import CRS

from api import *
from util.shapes import get_polygon_from_geojson
from process_sentinel1 import process_sentinel1
from process_sentinel2 import process_sentinel2


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
