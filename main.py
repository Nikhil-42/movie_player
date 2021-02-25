import cv2
from numba import jit
from numba.types import uint8
from scipy import spatial
import pandas as pd
import numpy as np
import hsluv
from progressbar import progressbar
import pathlib

avg_kern = np.ones((3, 2)) / 6

@jit(forceobj=True, cache=True)
def shrink_image(img, size=(164, 81)):
    scale = min(img.shape[0]/(size[1]*3), img.shape[1]/(size[0]*2))
    dim = (int(size[0] * 2 * scale), int(size[1] * 3 * scale))

    x_crop = int((img.shape[1] - dim[0]) / 2)
    y_crop = int((img.shape[0] - dim[1]) / 2)
    
    img = img[y_crop:-y_crop-1, x_crop:-x_crop-1, :]
    img = cv2.resize(img, (size[0]*2, size[1]*3))
    img = cv2.filter2D(img, -1, avg_kern, anchor=(0, 0))
    
    final = img[::3, ::2]
    return final

colors = spatial.cKDTree([
    [242, 128, 128],    # 0 [240, 240, 240],
    [196, 141, 197],    # 1 [ 51, 178, 242],
    [171, 179,  99],    # 2 [216, 127, 229],
    [186, 135,  93],    # 3 [242, 178, 153],
    [221, 113, 183],    # 4 [108, 222, 222],
    [191,  79, 199],    # 5 [ 25, 204, 127],
    [202, 155, 124],    # 6 [204, 178, 242],
    [ 82, 128, 128],    # 7 [ 76,  76,  76],
    [161, 128, 128],    # 8 [153, 153, 153],
    [152, 112, 108],    # 9 [178, 153,  76],
    [145, 181,  75],    # a [229, 102, 178],
    [115, 147,  70],    # b [204, 102,  51],
    [115, 134, 146],    # c [ 76, 102, 127],
    [157,  86, 166],    # d [ 78, 166,  87],
    [128, 179, 155],    # e [ 76,  76, 204],
    [ 12, 128, 128]     # f [ 17,  17,  17]
], balanced_tree=False)



hex = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
to_hex = np.vectorize(lambda x: hex[x])

jit_rgb_to_hsluv = jit(hsluv.rgb_to_hsluv, nopython=True, cache=True)
# @numba.guvectorize(['numba])


@jit(forceobj=True, cache=True)
def image_to_nfp(img):
    out = ''
    for y in range(img.shape[0]):
        color = colors.query(img[y])[1]
        out += ''.join(to_hex(color))  + '\n'
    return out[:-1]

if __name__ == '__main__':

    import tkinter as tk
    from tkinter import filedialog

    print("Movie file: ")
    root = tk.Tk()
    root.withdraw()

    movie_path = pathlib.Path(filedialog.askopenfilename()).absolute()

    if not movie_path.exists() or not movie_path.is_file():
        print("Invalid file")
        quit()

    save_path = pathlib.Path(str(movie_path.parent) + "/" + movie_path.stem).absolute()
    print("Writing frames to: ", save_path)

    import os
    if save_path.exists() and save_path.is_dir():
        import glob

        list_of_files = glob.glob('/path/to/folder/frame_*.nfp') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        i = int(''.join(filter(str.isdigit, latest_file)))
    else:
        os.makedirs(save_path)
        i = 0

    video = cv2.VideoCapture(str(movie_path))
    num_frames = 101263

    for count in progressbar(range(i, num_frames), min_value=0, max_value=num_frames):
        if not video.isOpened():
            break

        ret, frame = video.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        shrunk = shrink_image(frame)
        nfp_image = image_to_nfp(shrunk)
        
        with open(str(save_path) + '/frame_%d.nfp' % count, 'w') as f:
            f.write(nfp_image)

    video.release()

    import pdb; pdb.set_trace()
