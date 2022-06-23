import argparse
import os
import glob
from dotenv import load_dotenv

from api import *


def parse_command_line():
    """
    :return: The given arguments by the user parsed into a single namespace object.
    """
    parser = argparse.ArgumentParser(description='')

    # Define arguments passed on the command line.
    parser.add_argument('-start', '--start_date', help='Start date to look for images', required=True)
    parser.add_argument('-end', '--end_date', help='End date to look for images', required=True)

    # Parse all arguments given on the command line into a namespace object.
    args = parser.parse_args()

    return args


def process_sentinel2():
    pass


def process_sentinel1():
    pass


def main():
    # args = parse_command_line()
    load_dotenv()
    api = API(
        username=os.getenv('COPERNICUS_HUB_USERNAME'),
        password=os.getenv('COPERNICUS_HUB_PASSWORD'),
        footprint_pathname='../resources/study_area/Polygon_WGS84.geojson'
    )
    #sentinel1_products = api.get_sentinel1_products(date(2022, 1, 1), date(2022, 1, 7))
    sentinel2_products = api.get_sentinel2_products(date(2022, 1, 1), date(2022, 2, 27))

    for product_id in sentinel2_products:
        image = api.api.download(
            product_id,
            nodefilter=api.sentinel2_path_filter,
            directory_path='../resources/images/sentinel2')
        band11_path, band8_path, band3_path = glob.glob('../resources/images/sentinel2/**/*.jp2', recursive=True)
        # warp > remove image
        # get_image_data > remove warped image


if __name__ == '__main__':
    main()
