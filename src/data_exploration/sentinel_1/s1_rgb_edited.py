import os
from zipfile import ZipFile
import numpy as np
from osgeo import gdal
from src.util import get_study_area, get_image_data
os.chdir('C:\\Projects\\pooling-detection')

# I downloaded one S1 tile from https://search.asf.alaska.edu/#/?zoom=7.252&center=9.200,52.727&polygon=POLYGON((5.5751%2052.986,5.8622%2052.986,5.8622%2053.1695,5.5751%2053.1695,5.5751%2052.986))&start=2021-08-21T22:00:00Z&end=2021-08-24T21:59:59Z&flightDirs=Ascending&resultsLoaded=true&granule=S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894-GRD_HD
# https://appdividend.com/2022/01/19/python-unzip/#:~:text=To%20unzip%20a%20file%20in,inbuilt%20python%20module%20called%20zipfile.


def extract_tif_from_zip(zipfile_name, output_loc):
    """This function takes any zipfile looks for the tiff files that are in the zip. It
    creates a dictionary with the key-value pairs being the vv and vh and the opened
    versions of the tiffs using gdal.open()"""
    # Extract all the tiff files from a specified zip folder
    files = {}
    with ZipFile(zipfile_name, 'r') as zipObj:
        listOfFileNames = zipObj.namelist()
        current_tiff = 0
        for fileName in listOfFileNames:
            if fileName.endswith('.tiff'):
                # Extract a single file from zip
                file = zipObj.extract(fileName, output_loc)
                print('The TIFF file is extracted in the folder temp_tiff')
                key = 'vv' if current_tiff else 'vh'
                files[key] = gdal.Open(file)
                current_tiff += 1
        print(files)
    return files


def convert_to_decibel(vv_warp, vh_warp):
    """This function converts the vv and vh reprojected tiffs to decibels using the log 10
     while ignoring the 0 values caused by the masking to the study area"""
    vv_db = np.log10(vv_warp, out=np.zeros_like(vv_warp, dtype='float32'), where=(vv_warp != 0))
    vh_db = np.log10(vh_warp, out=np.zeros_like(vh_warp, dtype='float32'), where=(vh_warp != 0))
    print('The vv and vh files are converted to dB')
    return vv_db, vh_db


def calculate_ratio(vv_db, vh_db):
    """To get the third colour band for the RGB image, the ratio between the vv and vh decibels
    is taken. As we are working with logarithms, the ratio is simply a subtraction. It also checks
    that there are no -inf values, to check if the ratio calculation worked correctly."""
    vv_vh_ratio = vv_db - vh_db
    assert np.min(vv_vh_ratio) != -np.inf
    print('Calculating the vv/vh ratio done')
    return vv_vh_ratio


def min_max_norm(band):
    """"To be able to plot an RGB image, the three bands need to be stretched to accomodate
    correct RGB values. This is done by normalising each band."""
    band_min, band_max = band.min(), band.max()
    return (band - band_min) / (band_max - band_min)


def stack_arrays(vv, vh, ratio):
    """Create an array stack of the vv, vh and the vv/vh ratio to get the correct format
     for an RGB image."""
    s1_rgb = np.ma.stack((vv, vh, ratio))
    print('Stacking for rgb done')
    return s1_rgb


def main(zipfile):
    """This function calls on the functions above to extract vv and vh tiff files from a .zip,
     to convert them to dB, calculate the ratio, normalise and stack them, to be able to plot
     them as an RGB image."""
    zip_name = zipfile
    output_folder = 'src/data_exploration/sentinel_1/temp_tiff'

    #Extract tif files from a zip file
    files = extract_tif_from_zip(zip_name, output_folder)

    #Warp the files to EPSG:4326
    vh_warped = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vh_warp1.tiff', files['vh'], dstSRS="EPSG:4326")
    print('vh files are warped')
    vv_warped = gdal.Warp('src/data_exploration/sentinel_1/temp_tiff/vv_warp1.tiff', files['vv'], dstSRS="EPSG:4326")
    print('vv files are warped')

    #Get the study area
    study_area = get_study_area("resources/study_area/Polygon.geojson")

    #Get the data of only the study area from the warped tiff files
    vv, _ = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vv_warp1.tiff", study_area)
    vh, _ = get_image_data("src/data_exploration/sentinel_1/temp_tiff/vh_warp1.tiff", study_area)
    print('Image data study area acquired')

    #Convert backscatter to decibels
    vv_db, vh_db = convert_to_decibel(vv, vh)
    print('Conversion to dB complete')

    #Calculate VV / VH ratio
    vv_vh_ratio = calculate_ratio(vv_db, vh_db)
    print('vv/vh ratio calculated')

    #Normalise the three bands for RGB plotting
    vv_db_norm = min_max_norm(vv_db)
    vh_db_norm = min_max_norm(vh_db)
    ratio_norm = min_max_norm(vv_vh_ratio)
    print('Normalised the three bands')

    #Create a proper output name and place
    output_name = os.path.join(output_folder, zip_name.split("\\")[-1][:-4])
    output_name = output_name.replace("\\", "/")

    #Stack the normalised arrays
    s1_rgb = stack_arrays(vv_db_norm, vh_db_norm, ratio_norm)

    #Create a masked array of the array stack, where no data values become -999
    masked_band = np.ma.array(s1_rgb, mask=s1_rgb.mask, dtype=np.float32, fill_value=-999.)
    s1_rgb = masked_band.filled()
    s1_rgb = np.asarray(s1_rgb)
    print('s1 rgb stack is made')

    #Save the array stack and return the file name + extension
    np.save(output_name, s1_rgb)
    return output_name + '.npy'


if __name__ == '__main__':
    main()
