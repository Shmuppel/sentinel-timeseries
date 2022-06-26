import re

from products import Product


class Indice:
    def __init__(self, product: Product):
        self.product = product
        self.product.get_bands(self.path_filter)

    @staticmethod
    def path_filter(node_info: dict):
        pass

    def download(self):
        pass

    def calculate(self):
        pass


class NDWI_GAO(Indice):

    @staticmethod
    def path_filter(node_info):
        """ Only extract bands 03, 08, 11 """
        pattern = r"(.\/GRANULE\/.*\/R10m\/.*_B08_.*.jp2$|.\/GRANULE\/.*\/R20m\/.*_B11_.*.jp2$)"
        return bool(re.search(pattern, node_info['node_path']))

    def calculate(self):
        assert all((self.product.bands[8], self.product.bands[11])), "NDWI_GAO: Not all bands are downloaded"
        return (self.product.bands[8] - self.product.bands[11]) / (self.product.bands[8] + self.product.bands[11])
