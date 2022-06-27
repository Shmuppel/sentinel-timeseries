from band import Band
from products import Product


class Indice:
    BANDS = []

    def __init__(self, product: Product):
        self.product = product
        self.product.get_bands(self.BANDS)

    def calculate(self):
        pass


class NDWI_GAO(Indice):
    BANDS = (Band(mission='Sentinel2', number='08', spatial_resolution=20),
             Band(mission='Sentinel2', number='11', spatial_resolution=20))

    def calculate(self):
        return (self.product['08'] - self.product['11']) / (self.product['08'] + self.product['11'])


class NDWI_MCFEETER(Indice):
    BANDS = (Band(mission='Sentinel2', number='03', spatial_resolution=10),
             Band(mission='Sentinel2', number='08', spatial_resolution=10),)

    def calculate(self):
        return (self.product['03'] - self.product['08']) / (self.product['03'] + self.product['08'])


class MNDWI_XU(Indice):
    BANDS = (Band(mission='Sentinel2', number='03', spatial_resolution=10),
             Band(mission='Sentinel2', number='11', spatial_resolution=20),)

    def calculate(self):
        return (self.product['03'] - self.product['11']) / (self.product['03'] + self.product['11'])
