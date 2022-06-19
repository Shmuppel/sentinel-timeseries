
#load libraries
from rasterstats import zonal_stats
from rasterio.plot import show
from src.util import *
from src.data_exploration.sentinel_2.s2_indices import calculate_indices
import matplotlib.pyplot as plt
import shapely

#load parcels
parcelpath = "resources/study_area/BRP_AOI_RDNew.geojson"
parcels = get_study_area(parcelpath)

#polygon into geojson
transformer = pyproj.Transformer.from_crs(
    pyproj.CRS('EPSG:4326'),  # Assuming the study / crop area is in RD New
    pyproj.CRS('EPSG:28992'),  # The CRS as specified in the image
    always_xy=True).transform
parcels = transform(transformer, parcels)

#load indice maps
ndwi_gao, ndwi_mcfeeters, mndwi_xu, geometry_transform = calculate_indices()


#do some calculations with zonal_stats
masked_band = np.ma.array(ndwi_gao, mask=(ndwi_gao.mask), dtype=np.float32, fill_value=-999.)
masked_filled = masked_band.filled()

parcel_json = json.dumps(shapely.geometry.mapping(parcels))
#zonal_stats(parcel_json)
gao_stats = zonal_stats(parcel_json, masked_filled, affine = geometry_transform, nodata = -999.)

show(ndwi_gao, title='NDWI GAO', cmap='gist_ncar')
#show(parcels, title='NDWI GAO', cmap='gist_ncar')

#plt.show(parcels)

#xu_stats = zonal_stats(parcels, mndwi_xu, affine = geometry_transform)

#mcfeeters_stats = zonal_stats(parcels, ndwi_mcfeeters, affine = geometry_transform)