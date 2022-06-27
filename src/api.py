import time
import click
from datetime import date

import pyproj
import shapely.geometry
from sentinelsat import SentinelAPI

from products import Sentinel2Product


class SentinelTimeseriesAPI:
    """
    """

    def __init__(
            self,
            username: str,  # Copernicus open access hub username
            password: str,  # Copernicus open access hub password
            aoi: shapely.geometry.shape,  # A shapely geometry containing the area of interest
            warp: pyproj.CRS,  # Whether to warp the images to a specific CRS
            working_directory: str  # TODO this could be a default tempdir
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
        products = self.get_available_products(products)
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
        ) for product_id in self.get_available_products(products)]

    def check_available_products(
            self,
            products: dict[str, dict]
    ) -> tuple[list[str], list[str]]:
        """ Check how many items are available online, and how many will have to be accessed through LTA storage. """
        online_products, lta_products = [], []
        for key in products.keys():
            online_products.append(key) if self.api.is_online(key) else lta_products.append(key)
        print(f"API > {len(online_products)}/{len(online_products) + len(lta_products)} images directly downloadable online.")
        return online_products, lta_products

    def get_available_products(self, products: dict[str, dict]) -> list[str]:
        """
        Gets the Sentinel products that are online on the Copernicus Open Access Hub.
        Images that are available will be downloaded straight away, however some images may be in long term archival
        (LTA). An LTA image can be requested to come online by a user every 30min, and it may take up to 24hr for an
        LTA image to come online. On user approval this function will request images to come online without being
        rate limited, and it shall wait until all images are downloadable before continuing.
        """
        online_products, lta_products = self.check_available_products(products)
        # If there are not lta_products we can continue to download the online products.
        if not (n_lta_products := len(lta_products)): return online_products

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
