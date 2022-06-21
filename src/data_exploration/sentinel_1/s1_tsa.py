#### Import packages ####
from src.util import get_study_area, get_image_data
from src.data_exploration.sentinel_1.s1_rgb_edited import main

#### Get different files from API ####
#Put in list
S1_list = ...


#### Make RGB stacks of them using the main in S1_RGB -> s1_rgb_edited.py ####
RGB_list = []
for element in S1_list:{
    main(element)
    RGB_list = RGB_list + ...
}



#### Crop out the agricultural fields ####


#### Detect change in pixel values between the different images, use threshold ####


#### Plot pixels that changed with a corresponding time stamp ####
