from band import Band
from products import Sentinel2Product


class Indice:
    BANDS = []

    def __init__(self, product: Sentinel2Product):
        self.product = product
        self.product.get_bands(self.BANDS)
        self.product.mask_clouds_and_snow()

    def calculate(self):
        pass


class NDWI_GAO(Indice):
    BANDS = (Band(mission='Sentinel2', band='08', spatial_resolution=10),
             Band(mission='Sentinel2', band='11', spatial_resolution=20))

    def calculate(self):
        return (self.product['08'] - self.product['11']) / (self.product['08'] + self.product['11'])


class NDWI_MCFEETER(Indice):
    BANDS = (Band(mission='Sentinel2', band='03', spatial_resolution=10),
             Band(mission='Sentinel2', band='08', spatial_resolution=10),)

    def calculate(self):
        return (self.product['03'] - self.product['08']) / (self.product['03'] + self.product['08'])


class MNDWI_XU(Indice):
    BANDS = (Band(mission='Sentinel2', band='03', spatial_resolution=10),
             Band(mission='Sentinel2', band='11', spatial_resolution=20),)

    def calculate(self):
        return (self.product['03'] - self.product['11']) / (self.product['03'] + self.product['11'])
