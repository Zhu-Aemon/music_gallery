import numpy as np
from PIL import Image
from noise import pnoise2
from Gallery import Core
import os
from tqdm import tqdm

# sizeOfImage = 256
#
# perlin = np.empty((sizeOfImage, sizeOfImage), dtype=np.float32)
# freq = 1024
# for y in range(256):
#     for x in range(256):
#         perlin[y][x] = pnoise2(x / freq, y / freq, 4)  # don't need to scale or shift here as the code below undoes that anyway
# max_array = np.amax(perlin)
# min_array = np.amin(perlin)
# max_array -= min_array
# perlin -= min_array
# perlin /= max_array
# perlin *= 255
# img = Image.fromarray(perlin.astype('uint8'), 'RGB')  # convert to int here instead
# img.save('test.png')

Core.save_cover(r"D:\Music\She Her Her Hers - Episode 33.mp3", 'example.jpg')
# img = Image.open('example.jpg')
# array = np.array(img)


def array_mean(array_3d, x, y, blur_pixel):
    x_length = array_3d.shape[0]
    y_length = array_3d.shape[1]
    x_start = max(0, x - blur_pixel)
    x_end = min(x_length, x + blur_pixel)
    y_start = max(0, y - blur_pixel)
    y_end = min(y_length, y + blur_pixel)
    # pixel_number = (x_end - x_start) * (y_end - y_start)
    # array_total = np.array([0, 0, 0])
    # for i in range(x_start, x_end):
    #     for j in range(y_start, y_end):
    #         array_total += array_3d[i][j]
    return np.mean(np.mean(array_3d[x_start: x_end, y_start: y_end], axis=1), axis=0)


def image_blur(filepath, blur_pixel):
    image = Image.open(filepath)
    array = np.array(image)
    output_array = np.zeros(array.shape)
    for x in tqdm(range(array.shape[0])):
        for y in range(array.shape[1]):
            output_array[x][y] = array_mean(array, x, y, blur_pixel)
    return output_array


output = image_blur('example.jpg', 50)
output_image = Image.fromarray(output.astype('uint8'), 'RGB')
output_image.save('output.jpg')
