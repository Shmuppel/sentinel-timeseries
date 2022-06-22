# Import packages
import os
import numpy as np
from matplotlib import pyplot as plt
from src.data_exploration.sentinel_1.s1_rgb_edited import main

# Get different files from API
# Put in dictionary
os.chdir('C:\\Projects\\pooling-detection')
zip1 = 'E:\ACt\S1A_IW_GRDH_1SDV_20210818T171714_20210818T171739_039287_04A39F_A07A.zip'
zip2 = 'E:\ACt\S1A_IW_GRDH_1SDV_20210823T172521_20210823T172546_039360_04A618_4894.zip'
zip3 = 'E:\ACt\S1B_IW_GRDH_1SDV_20210824T171645_20210824T171710_028391_036337_CA81.zip'
S1_dict = {1: zip1, 2: zip2, 3: zip3}


# Make RGB stacks of them using the main in S1_RGB -> s1_rgb_edited.py
def RGB_dict(input_dict):
    rgb_dictionary = {}
    for value in input_dict.values():
        rgb_s1 = main(value)
        rgb_dictionary['RGB_' + str(enumerate(value))] = rgb_s1
    print(rgb_dictionary)
    return rgb_dictionary
rgbs = RGB_dict(S1_dict)


# Detect change in pixel values between the different images, use threshold
#Stack as 4D
#https://stackoverflow.com/questions/58784949/combine-3d-arrays-into-a-4d-array-in-numpy
array_stack = []
for key, value in rgbs.items():
    array_stack.append(np.load(value).T)
    print('np loaded')

#Plot the individual images
for i in range(0, 3):
    plt.imshow(array_stack[i])
    plt.figure(i+1)
    plt.title(i)
    plt.show()

#Images not equal in size so I can't stack them
stack_4d = np.vstack((array_stack[0], array_stack[1], array_stack[2]))


# Plot pixels that changed with a corresponding time stamp
