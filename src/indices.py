import re

from products import Product


class Indice:
    PATH_REGEX = r""

    def __init__(self, product: Product):
        self.product = product
        self.product.get_bands(self.path_filter)

    def path_filter(self, node_info: dict):
        pattern = self.PATH_REGEX
        return bool(re.search(pattern, node_info['node_path']))

    def get_affine_transform(self):
        pass

    def calculate(self):
        pass


class NDWI_GAO(Indice):
    PATH_REGEX = r"(.\/GRANULE\/.*\/R10m\/.*_B08_.*.jp2$|.\/GRANULE\/.*\/R20m\/.*_B11_.*.jp2$)"

    def get_affine_transform(self):
        return self.product[8].array_affine_transform

    def calculate(self):
        return (self.product[8] - self.product[11]) / (self.product[8] + self.product[11])


class NDWI_MCFEETER(Indice):
    PATH_REGEX = r"(.\/GRANULE\/.*\/R10m\/.*_B0[38]_.*.jp2$)"

    def get_affine_transform(self):
        return self.product[3].array_affine_transform

    def calculate(self):
        return (self.product[3] - self.product[8]) / (self.product[3] + self.product[8])


class MNDWI_XU(Indice):
    PATH_REGEX = r"(.\/GRANULE\/.*\/R10m\/.*_B03_.*.jp2$|.\/GRANULE\/.*\/R20m\/.*_B11_.*.jp2$)"

    def get_affine_transform(self):
        return self.product[3].array_affine_transform

    def calculate(self):
        return (self.product[3] - self.product[11]) / (self.product[3] + self.product[11])
