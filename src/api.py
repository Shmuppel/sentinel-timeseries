import re
import time
import click
from datetime import date

import pyproj
import shapely.geometry
from sentinelsat import SentinelAPI

from products import Sentinel2Product


class NearRealtimeAPI:
    """
    """

    def __init__(
            self,
            username: str,
            password: str,
            aoi: shapely.geometry.shape,
            warp: pyproj.CRS,
            working_directory: str
    ):
        self.api = SentinelAPI(username, password)
        self.aoi = aoi
        self.warp = warp
        self.working_directory = working_directory

    def get_sentinel1_products(
            self,
            start_date: date,
            end_date: date
    ) -> list[str]:
        """
        """
        products = self.api.query(self.aoi.wkt,
                                  date=(start_date, end_date),
                                  producttype='GRD',
                                  orbitdirection='ASCENDING',
                                  platformname='Sentinel-1')
        products = self.check_products(products)
        return products

    def get_sentinel2_products(
            self,
            start_date: date,
            end_date: date,
            cloudcover: tuple[int] = (0, 5),
    ) -> list[Sentinel2Product]:
        """
        """
        products = self.api.query(self.aoi.wkt,
                                  date=(start_date, end_date),
                                  processinglevel='Level-2A',
                                  platformname='Sentinel-2',
                                  cloudcoverpercentage=cloudcover)
        return [Sentinel2Product(
            api=self.api,
            product_id=product_id,
            aoi=self.aoi,
            warp=self.warp,
            working_directory=self.working_directory
        ) for product_id in self.check_products(products)]

    def check_available_products(
            self,
            products: dict[str, dict]
    ) -> tuple[list[str], list[str]]:
        """
        """
        online_products, lta_products = [], []
        # Check how many items are available online, and how many will have to be accessed through LTA storage.
        for key in products.keys():
            online_products.append(key) if self.api.is_online(key) else lta_products.append(key)
        print(f"API > {len(online_products)}/{len(online_products) + len(lta_products)} images directly downloadable online.")
        return online_products, lta_products

    def check_products(
            self,
            products: dict[str, dict]
    ) -> list[str]:
        """
        """
        online_products, lta_products = self.check_available_products(products)
        # If there are not lta_products we can continue to download the online products.
        if not (n_lta_products := len(lta_products)):
            return online_products

        # If there are any images unavailable, prompt the user if he wants to go through with LTA retrieval
        if click.confirm(f"{n_lta_products} images in long term archival, retrieve them in 30min increments? (y/n): "):
            print(f'API > Retrieving {n_lta_products} long term archival images...')
            for index, key in enumerate(lta_products):
                print(f'API > Retrieved {key} from long term storage ({index + 1}/{n_lta_products})')
                self.api.trigger_offline_retrieval(key)
                if index + 1 != n_lta_products: time.sleep(1800)

            while len(lta_products) != 0:
                print(f'API > Waiting till {len(lta_products)} images come online this can take up to 24 hours...')
                online_products, lta_products = self.check_available_products(products)
                if lta_products: time.sleep(900)

        return online_products

    @staticmethod
    def sentinel1_path_filter(node_info: dict) -> bool:
        """ Only extract grd vv and vh bands """
        pattern = r".\/measurement\/s1a-.*-grd-(vh|vv)-.*\.tiff$"
        return bool(re.search(pattern, node_info['node_path']))

    @staticmethod
    def sentinel2_path_filter(node_info: dict) -> bool:
        """ Only extract bands 03, 08, 11 """
        pattern = r"(.\/GRANULE\/.*\/R10m\/.*_B0[38]_.*.jp2$|.\/GRANULE\/.*\/R20m\/.*_B11_.*.jp2$)"
        return bool(re.search(pattern, node_info['node_path']))
