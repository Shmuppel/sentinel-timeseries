from datetime import date

from band import Band


def process_sentinel1_rgb(api, parcels):
    sentinel1_products = api.get_sentinel1_products(date(2022, 1, 1), date(2022, 1, 7))
    for product in sentinel1_products:
        product.get_bands([Band(mission='Sentinel1', band='VV'), Band(mission='Sentinel1', band='VH')])
        # product['VV'].array
        # product['VH'].array
