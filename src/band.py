from typing import *


class Band:
    def __init__(
            self,
            mission: str,
            number: Union[str, int],
            spatial_resolution: int,
            path: Optional[str] = None
    ):
        self.mission = mission
        self.number = self.normalize_band_number(number)
        self.spatial_resolution = spatial_resolution
        self.path = path
        self.array = None
        self.array_affine_transform = None

    def normalize_band_number(self, number: Union[str, int]) -> str:
        """
        Normalize the band numbers to a common format with leading zeros.
        This makes sure the band number correlates to the one in the product path.
        """
        if number == '8a': return number
        return '0' + str(int(number)) if int(number) < 10 else str(int(number))

    def get_path_filter(self) -> str:
        """
        """
        if self.mission == 'Sentinel2':
            return rf"./GRANULE\/.*/R{self.spatial_resolution}m/.*_B{self.number}_.*.jp2$"
        if self.mission == 'Sentinel1':
            # r".\/measurement\/s1a-.*-grd-(vh|vv)-.*\.tiff$"
            raise NotImplementedError

    def __add__(self, other):
        return self.array + other.array

    def __sub__(self, other):
        return self.array - other.array

    def __mul__(self, other):
        return self.array * other.array

