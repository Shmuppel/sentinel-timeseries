# First try at git commit
#Link to Sentinel 1 Image 23-08-2021
# s3://sentinel-s1-l1c/GRD/2021/8/23/IW/DV/S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894/

# I downloaded one S1 tile from https://search.asf.alaska.edu/#/?zoom=7.252&center=9.200,52.727&polygon=POLYGON((5.5751%2052.986,5.8622%2052.986,5.8622%2053.1695,5.5751%2053.1695,5.5751%2052.986))&start=2021-08-21T22:00:00Z&end=2021-08-24T21:59:59Z&flightDirs=Ascending&resultsLoaded=true&granule=S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894-GRD_HD
# https://appdividend.com/2022/01/19/python-unzip/#:~:text=To%20unzip%20a%20file%20in,inbuilt%20python%20module%20called%20zipfile.
from zipfile import ZipFile
with ZipFile('E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip', 'r') as zipObj:
    # Extract all the contents of zip file in current directory
    zipObj.extractall()


