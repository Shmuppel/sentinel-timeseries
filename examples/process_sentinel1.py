from datetime import date
import numpy as np

from rasterio.plot import show
from sentineltimeseries.util.arrays import get_band_as_array


def convert_to_decibel(band):
    """This function converts the vv and vh reprojected tiffs to decibels using the log 10
     while ignoring the 0 values caused by the masking to the study area"""
    return np.log10(band, out=np.zeros_like(band, dtype='float32'), where=(band != 0))


def min_max_norm(band):
    """"To be able to plot an RGB image, the three bands need to be stretched to accommodate
    correct RGB values. This is done by normalising each band."""
    band_min, band_max = band.min(), band.max()
    return (band - band_min) / (band_max - band_min)


def process_sentinel1(api, parcels):
    sentinel1_products = api.get_sentinel1_products(date(2022, 1, 1), date(2022, 1, 7))
    for product in sentinel1_products:
        vv, _ = get_band_as_array(product['VV'].path, api.aoi)
        vh, affine_transform = get_band_as_array(product['VH'].path, api.aoi)

        vv_db, vh_db = convert_to_decibel(vv), convert_to_decibel(vh)
        vv_vh_ratio = vv_db - vh_db
        # check that there are no -inf values, else the calculations did not go correctly.
        assert np.min(vv_vh_ratio) != -np.inf

        vv_db_norm = min_max_norm(vv_db)
        vh_db_norm = min_max_norm(vh_db)
        ratio_norm = min_max_norm(vv_vh_ratio)
        print('Normalised the three bands')

        # Stack the normalised arrays
        s1_rgb = np.ma.stack((vv_db_norm, vh_db_norm, ratio_norm))

        # Turn masked arrays into normal arrays because masked arrays are not supported when saving to file or plotting
        masked_band = np.ma.array(s1_rgb, mask=s1_rgb.mask, dtype=np.float32, fill_value=-999.)
        s1_rgb = masked_band.filled()
        s1_rgb = np.asarray(s1_rgb)
        show(s1_rgb)


