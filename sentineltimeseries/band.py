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

    def get_path_filter(self) -> str:
        """
        """
        if self.mission == 'Sentinel1':
            return rf"./measurement/s1a-.*-grd-{self.name.lower()}-.*\.tiff$"

        if self.mission == 'Sentinel2':
            if self.name == 'CLD': return f'.*MSK_CLDPRB_{self.spatial_resolution}m.jp2'
            if self.name == 'SNW': return f'.*MSK_SNWPRB_{self.spatial_resolution}m.jp2'
            return rf"./GRANULE/.*/R{self.spatial_resolution}m/.*_{self.name}_.*.jp2$"
