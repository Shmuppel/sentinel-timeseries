from typing import *


class Band:
    def __init__(
            self,
            mission: str,
            band: Union[str, int],
            spatial_resolution: int,
            path: Optional[str] = None
    ):
        self.mission = mission
        self.band = self.normalize_band_name(band)
        self.spatial_resolution = spatial_resolution
        self.path = path
        self.array = None
        self.array_affine_transform = None

    def normalize_band_name(self, band: Union[str, int]) -> str:
        """
        Normalize the bands to a common format with leading zeros.
        This makes sure the band correlates to the one in the product path.
        """
        if band == '8a': return band
        return '0' + str(int(band)) if int(band) < 10 else str(int(band))

    def get_path_filter(self) -> str:
        """
        """
        if self.mission == 'Sentinel2':
            return rf"./GRANULE\/.*/R{self.spatial_resolution}m/.*_B{self.band}_.*.jp2$"
        if self.mission == 'Sentinel1':
            # r".\/measurement\/s1a-.*-grd-(vh|vv)-.*\.tiff$"
            raise NotImplementedError

    def __bool__(self):
        return self.array is not None

    def __add__(self, other):
        return self.array + other.array

    def __sub__(self, other):
        return self.array - other.array

    def __mul__(self, other):
        return self.array * other.array

