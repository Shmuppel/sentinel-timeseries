import glob
import os
import re
import shutil
from abc import ABC
import numpy as np
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
        self.working_directory = f'{working_directory}/{self.product_id}'  # Directory to read and write temporary images
        self.bands = {}  # Holds the actual product measurements
        os.makedirs(self.working_directory, exist_ok=True)

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
        warped_dir = f'{self.working_directory}/warped/'
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
        # Cloud and Snow masks are tiny and would only match Sentinel 2 imagery.
        path_filters = ['.*MSK_CLDPRB_20m.jp2', '.*MSK_SNWPRB_20m.jp2']
        path_filters.extend([band.get_path_filter() for band in bands])
        path_filter_pattern = rf"({'|'.join(path_filters)})"

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

    def remove(self):
        shutil.rmtree(f'{self.working_directory}')
        os.mkdir(f'{self.working_directory}/{self.product_id}')

    def __getitem__(self, key):
        return self.bands[key]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.remove()


class Sentinel2Product(Product):

    def create_bands(self):
        band_paths = glob.glob(f'{self.working_directory}/**/*.jp2', recursive=True)
        for band_file_path in band_paths:
            band_path = band_file_path.replace(self.working_directory, '')
            band_path_split = band_path.split('_')
            band_number = band_path_split[-2]  # B03, SNWPRB, CLDPRB
            band_number = band_number[1:] if band_number.startswith('B') else band_number[:-3]  # 03, SNW, CLD
            spatial_resolution = int(band_path_split[-1][:-5])
            if band_number in self.bands.keys(): continue

            self.bands[band_number] = Band(
                mission='Sentinel2',
                band=band_number,
                path=band_file_path,
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

    def mask_clouds_and_snow(self):
        assert all((self.bands['CLD'], self.bands['SNW']))
        clouds, snow = self.bands['CLD'].array, self.bands['SNW'].array
        for band in self.bands.values():
            if band.band == 'CLD' or band.band == 'SNW': continue
            band.array = np.ma.array(band.array,
                                     mask=((clouds > 0) | (snow > 0) | band.array.mask),
                                     dtype=np.float32,
                                     fill_value=-999)


class Sentinel1Product(Product):

    def create_bands(self):
        band_paths = glob.glob(f'{self.working_directory}/**/*.tiff', recursive=True)
        for band_file_path in band_paths:
            band_path = band_file_path.replace(self.working_directory, '')
            band_path_split = band_path.split('-')
            band_number = band_path_split[3].upper()  # VV, VH
            if band_number in self.bands.keys(): continue
            self.bands[band_number] = Band(
                mission='Sentinel1',
                band=band_number,
                path=band_file_path,
            )

    def get_arrays(self):
        bands = [band for band in self.bands.values()]
        for band in bands:
            if band.array is not None: continue  # Already got the array of this band
            band.array, band.array_affine_transform = get_image_data(band.path, self.aoi)
