import glob
import os
import re
import shutil
from abc import ABC
from typing import Union

import pyproj
from osgeo import gdal

from .band import Band


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
        self.working_directory = os.path.join(working_directory, self.product_id)
        self.bands = {}  # Holds the actual product measurements
        os.makedirs(self.working_directory, exist_ok=True)

    def warp_band(self, band: Band):
        """
        """
        warped_dir = os.path.join(self.working_directory, 'warped')
        os.makedirs(warped_dir, exist_ok=True)
        warped_band_path = f'{warped_dir}/{band.name}.tiff'
        # Only if a previous run did not already warp the band.
        if not os.path.exists(warped_band_path):
            print(f'Product {self.product_id}: warping band {band.name} to EPSG:{self.warp.to_epsg()}...')
            gdal.Warp(warped_band_path, band.path, dstSRS=f'EPSG:{self.warp.to_epsg()}')
        band.path = warped_band_path

    def get_band(self, band: Union[Band, str]):
        """
        """
        if type(band) == str: return self.__getitem__(band)
        path_filter = band.get_path_filter()
        self.api.download(
            self.product_id,
            nodefilter=lambda node_info: bool(re.search(path_filter, node_info['node_path'])),
            directory_path=self.working_directory
        )
        self.set_band_file_path(band)
        if self.warp: self.warp_band(band)
        return band

    def set_band_file_path(self, band: Band):
        pass

    def remove(self):
        """ """
        shutil.rmtree(f'{self.working_directory}')
        os.mkdir(f'{self.working_directory}/{self.product_id}')

    def __getitem__(self, band_name: Union[tuple[str], str]):
        """ """
        # If there are multiple bands being passed, just call __getitem__ for each of them.
        if type(band_name) == tuple: return list(self.__getitem__(band) for band in band_name)
        band_options = self.bands.keys()
        if band_name not in band_options: raise KeyError(f"Invalid band name {band_name}, options are: {band_options}")
        band = self.bands[band_name]
        return self.get_band(band)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.remove()


class Sentinel2Product(Product):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bands = {
            'B01': Band(mission='Sentinel2', name='B01', spatial_resolution=60),
            'B02': Band(mission='Sentinel2', name='B02', spatial_resolution=10),
            'B03': Band(mission='Sentinel2', name='B03', spatial_resolution=10),
            'B04': Band(mission='Sentinel2', name='B04', spatial_resolution=10),
            'B05': Band(mission='Sentinel2', name='B05', spatial_resolution=20),
            'B06': Band(mission='Sentinel2', name='B06', spatial_resolution=20),
            'B07': Band(mission='Sentinel2', name='B07', spatial_resolution=20),
            'B08': Band(mission='Sentinel2', name='B08', spatial_resolution=10),
            'B8a': Band(mission='Sentinel2', name='B8a', spatial_resolution=20),
            'B09': Band(mission='Sentinel2', name='B09', spatial_resolution=60),
            'B10': Band(mission='Sentinel2', name='B10', spatial_resolution=60),
            'B11': Band(mission='Sentinel2', name='B11', spatial_resolution=20),
            'B12': Band(mission='Sentinel2', name='B12', spatial_resolution=20),
            'CLD': Band(mission='Sentinel2', name='CLD', spatial_resolution=20),
            'SNW': Band(mission='Sentinel2', name='SNW', spatial_resolution=20),
        }

    def set_band_file_path(self, band: Band):
        """
        TODO This is an iterative solution, it may be possible to deduce the file path based on
        the metadata returned from self.api.download as well. That may also be generalizable
        across products, if so you would only need a single set_band_file_path function.
        """
        band_paths = glob.glob(f'{self.working_directory}/**/*.jp2', recursive=True)
        for band_file_path in band_paths:
            # Disregard working directory as it would affect splicing indices.
            band_path = band_file_path.replace(self.working_directory, '')
            if band_path.startswith('/warped'): continue
            band_path_split = band_path.split('_')

            band_name = band_path_split[-2]  # e.g. B03, SNWPRB, CLDPRB
            if not band_name.startswith('B'): band_name = band_name[:-3]  # e.g. SNW, CLD
            if band.name != band_name: continue
            spatial_resolution = int(band_path_split[-1][:-5])

            band.path = band_file_path
            band.spatial_resolution = spatial_resolution


class Sentinel1Product(Product):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bands = {
            'VV': Band(mission='Sentinel1', name='VV'),
            'VH': Band(mission='Sentinel1', name='VH'),
        }

    def set_band_file_path(self, band: Band):
        band_paths = glob.glob(f'{self.working_directory}/**/*.tiff', recursive=True)
        for band_file_path in band_paths:
            # Disregard working directory as it would affect splicing indices.
            band_path = band_file_path.replace(self.working_directory, '')
            if band_path.startswith('/warped'): continue
            band_path_split = band_path.split('-')
            band_name = band_path_split[3].upper()  # VV, VH
            if band.name != band_name: continue
            band.path = band_file_path
