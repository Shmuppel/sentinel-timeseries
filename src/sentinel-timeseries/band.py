from typing import *


class Band:
    def __init__(
            self,
            mission: str,
            name: Union[str, int],
            spatial_resolution: int = None,
            path: Optional[str] = None
    ):
        self.mission = mission
        self.name = name
        self.spatial_resolution = spatial_resolution
        self.path = path
        self.array = None
        self.array_affine_transform = None

    def get_path_filter(self) -> str:
        """
        """
        if self.mission == 'Sentinel2':
            return rf"./GRANULE\/.*/R{self.spatial_resolution}m/.*_{self.name}_.*.jp2$"
        if self.mission == 'Sentinel1':
            return rf"./measurement/s1a-.*-grd-{self.name.lower()}-.*\.tiff$"

    def __bool__(self):
        return self.array is not None

    def __add__(self, other):
        return self.array + other.array

    def __sub__(self, other):
        return self.array - other.array

    def __mul__(self, other):
        return self.array * other.array
