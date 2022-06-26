import glob
import os
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
        self.warp = warp
        self.working_directory = working_directory
        self.bands = {}

    def create_bands(self):
        pass

    def get_arrays(self):
        pass

    def warp_bands(self):
        warped_dir = f'{self.working_directory}/warped/{self.product_id}'
        os.makedirs(warped_dir, exist_ok=True)
        for band_name, band in self.bands.items():
            if not band: continue
            warped_band_path = f'{warped_dir}/{band.name}.tiff'
            gdal.Warp(warped_band_path, band.path, dstSRS=f'EPSG:{self.warp.to_epsg()}')
            band.path = warped_band_path

    def get_bands(self, path_filter):
        image_metadata = self.api.download(self.product_id,
                                           nodefilter=path_filter,
                                           directory_path=self.working_directory)
        date = image_metadata['date'].strftime("%Y/%m/%d")
        self.create_bands()
        if self.warp: self.warp_bands()
        self.get_arrays()


class Sentinel2Product(Product):

    def create_bands(self):
        band_paths = glob.glob(f'{self.working_directory}/**/*.jp2', recursive=True)
        for band_path in band_paths:
            spatial_resolution = int(band_path[-7:-5])
            band_name = int(band_path[-10:-8])
            self.bands[band_name] = Band(name=band_name, path=band_path, spatial_resolution=spatial_resolution)

    def get_arrays(self):
        bands = [band for _, band in self.bands.items() if band]
        bands.sort(key=lambda band: band.spatial_resolution)
        resample = None
        for band in bands:
            band.array, band.array_affine_transform = get_image_data(band.path, self.aoi, resample)
            if not resample: resample = band.array.shape


class Sentinel1Product(Product):

    def create_bands(self):
        raise NotImplementedError

    def get_arrays(self):
        raise NotImplementedError

