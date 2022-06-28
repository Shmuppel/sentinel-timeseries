file1 = r"C:\Users\soria\OneDrive\Documents\Universiteit\Leerjaar 5\Periode 6 (ACT)\Berner-sennen-puppys-algemene-informatie-en-introductie.jpg"
file2 = r"C:\Users\soria\OneDrive\Documents\Universiteit\Leerjaar 5\Periode 6 (ACT)\MindandBeauty.nl_Berner_Sennen_puppy_update_maart_2019_1.png"
filenames = [file1, file2]

#imageio.imwrite() to write np array as image

import imageio
with imageio.get_writer('/src/data_exploration/sentinel_1/movie.gif', mode='I') as writer:
    for filename in filenames:
        image = imageio.v2.imread(filename)
        writer.append_data(image)


import imageio.v3 as iio
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

gif_path = "/src/data_exploration/sentinel_1/test.gif"
frames_path = "/src/data_exploration/sentinel_1/{i}.jpg"
#plt.figure(figsize=(4,4))
for filename in filenames:
    image = mpimg.imread(filename)
    plt.imshow(image)
    plt.savefig(r"/src/data_exploration/sentinel_1/{filename}.jpg")

frames = np.stack(
    [iio.imread(f"{filename}.jpg") for i in range(len(filenames))],
    axis=0
)

iio.imwrite(gif_path, frames, mode="I")

