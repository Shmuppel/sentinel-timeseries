import re
import time
import click
from datetime import date
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt


class API:

    def __init__(self, username, password, footprint_pathname):
        self.footprint = geojson_to_wkt(read_geojson(footprint_pathname))
        self.api = SentinelAPI(username, password)

    def get_sentinel1_products(
            self,
            start_date: date,
            end_date: date
    ) -> list[str]:
        products = self.api.query(self.footprint,
                                  date=(start_date, end_date),
                                  producttype='GRD',
                                  orbitdirection='ASCENDING',
                                  platformname='Sentinel-1')
        products = self.check_products(products)
        return products

    def get_sentinel2_products(
            self,
            start_date: date,
            end_date: date
    ) -> list[str]:
        products = self.api.query(self.footprint,
                                  date=(start_date, end_date),
                                  processinglevel='Level-2A',
                                  platformname='Sentinel-2',
                                  cloudcoverpercentage=(0, 5))
        products = self.check_products(products)
        return products

    def check_available_products(
            self,
            products: dict[str, dict]
    ) -> tuple[list[str], list[str]]:
        online_products, lta_products = [], []
        # Check how many items are available online, and how many will have to be accessed through LTA storage.
        for key in products.keys():
            online_products.append(key) if self.api.is_online(key) else lta_products.append(key)
        print(
            f"API > {len(online_products)}/{len(online_products) + len(lta_products)} images directly downloadable online.")
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
