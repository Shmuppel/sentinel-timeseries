import os
import imageio


def create_gif_from_images(image_dir, out_path, fps=1):
    images = []
    for file_name in sorted(os.listdir(image_dir)):
        file_path = os.path.join(image_dir, file_name)
        images.append(imageio.imread(file_path))
    imageio.mimsave(out_path, images, fps=fps)
