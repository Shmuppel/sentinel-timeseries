def get_arrays(self):
    bands = [band for band in self.bands.values()]
    bands.sort(key=lambda band: band.spatial_resolution)
    resample = None
    for band in bands:
        if band.array is not None: continue  # Already got the array of this band
        band.array, band.array_affine_transform = get_image_data(band.path, self.aoi, resample)
        if not resample: resample = band.array.shape


def mask_clouds_and_snow(self):
    assert all((self.bands['CLD'], self.bands['SNW']))
    clouds, snow = self.bands['CLD'].array, self.bands['SNW'].array
    for band in self.bands.values():
        if band.band == 'CLD' or band.band == 'SNW': continue
        band.array = np.ma.array(band.array,
                                 mask=((clouds > 0) | (snow > 0) | band.array.mask),
                                 dtype=np.float32,
                                 fill_value=-999)

    def get_cloud_and_snow_mask(self):
        path_filters = ['.*MSK_CLDPRB_20m.jp2', '.*MSK_SNWPRB_20m.jp2']
        filter_pattern = self.get_grouped_regex_pattern(path_filters)
        path_filter =
        self.api.download(
            self.product_id,
            nodefilter=lambda node_info: bool(re.search(filter_pattern, node_info['node_path'])),
            directory_path=self.working_directory
        )


    def get_arrays(self):
        bands = [band for band in self.bands.values()]
        for band in bands:
            if band.array is not None: continue  # Already got the array of this band
            band.array, band.array_affine_transform = get_image_data(band.path, self.aoi)
