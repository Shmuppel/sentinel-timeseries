import glob
import os
import re
import shutil
from abc import ABC

import pyproj
from osgeo import gdal

from band import Band
from util import get_image_data


class Product(ABC):

    def __init__(
            self,
            api,
            product_id: str,
            aoi: dict,
            working_directory: str,
            warp: pyproj.CRS = None,
    ):
        self.api = api
        self.product_id = product_id
        self.aoi = aoi
        self.warp = warp  # Whether the images should be warped to a CRS before processing
        self.working_directory = working_directory  # Directory to read and write temporary images
        self.bands = {}  # Holds the actual product measurements

    def create_bands(self):
        """
        """
        pass

    def get_arrays(self):
        """
        """
        pass

    def warp_bands(self):
        """
        """
        warped_dir = f'{self.working_directory}/warped/{self.product_id}'
        os.makedirs(warped_dir, exist_ok=True)
        for band in self.bands.values():
            warped_band_path = f'{warped_dir}/{band.band}.tiff'
            if os.path.exists(warped_band_path):
                band.path = warped_band_path
                continue
            print(f'Product {self.product_id}: warping band {band.band} to EPSG:{self.warp.to_epsg()}...')
            gdal.Warp(warped_band_path, band.path, dstSRS=f'EPSG:{self.warp.to_epsg()}')
            band.path = warped_band_path

    def get_bands(self, bands: list[Band]):
        """
        """
        path_filter_pattern = rf"({'|'.join([band.get_path_filter() for band in bands])})"
        self.api.download(
            self.product_id,
            nodefilter=lambda node_info: bool(re.search(path_filter_pattern, node_info['node_path'])),
            directory_path=self.working_directory
        )
        self.create_bands()
        if not all([band.band in self.bands.keys() for band in bands]):
            raise ValueError("Not all bands were downloaded, make sure the combination of band and spatial resolution exists.")
        if self.warp: self.warp_bands()
        self.get_arrays()

    def __getitem__(self, key):
        return self.bands[key]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        shutil.rmtree(f'{self.working_directory}')
        os.mkdir(f'{self.working_directory}')


class Sentinel2Product(Product):

    def create_bands(self):
        band_paths = glob.glob(f'{self.working_directory}/**/*.jp2', recursive=True)
        for band_path in band_paths:
            band_number = band_path[-10:-8]
            spatial_resolution = int(band_path[-7:-5])
            if band_number in self.bands.keys(): continue
            self.bands[band_number] = Band(
                mission='Sentinel2',
                band=band_number,
                path=band_path,
                spatial_resolution=spatial_resolution
            )

    def get_arrays(self):
        bands = [band for band in self.bands.values()]
        bands.sort(key=lambda band: band.spatial_resolution)
        resample = None
        for band in bands:
            if band.array is not None: continue  # Already got the array of this band
            band.array, band.array_affine_transform = get_image_data(band.path, self.aoi, resample)
            if not resample: resample = band.array.shape


class Sentinel1Product(Product):

    def create_bands(self):
        raise NotImplementedError

    def get_arrays(self):
        raise NotImplementedError

