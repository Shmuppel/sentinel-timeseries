"""
This is Sentinel 1 image processing for calculating indexes in order to find out pooling with radar!
"""

# 1. Find Sentinel-2 cloud free images with clear pooling.
# 2. Clip the water pixel with a `Water Index(es)`.
# 3. Check the same areas/pixes for the dB values.
# 4. Use an average calculation to create `water pixel index` in
#    the following format: min <= value <= max
