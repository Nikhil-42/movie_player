import cv2
from numba import jit
from scipy import spatial
import numpy as np
from progressbar import progressbar
import pathlib

color_space = cv2.COLOR_BGR2LAB
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

colors_arr = cv2.cvtColor(np.array([
    [240, 240, 240],
    [ 51, 178, 242],
    [216, 127, 229],
    [242, 178, 153],
    [108, 222, 222],
    [ 25, 204, 127],
    [204, 178, 242],
    [ 76,  76,  76],
    [153, 153, 153],
    [178, 153,  76],
    [229, 102, 178],
    [204, 102,  51],
    [ 76, 102, 127],
    [ 78, 166,  87],
    [ 76,  76, 204],
    [ 17,  17,  17]
], dtype='uint8').reshape((16, 1, 3)), color_space).reshape((16, 3))
colors = spatial.cKDTree(colors_arr, balanced_tree=True)

hex = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
to_hex = np.vectorize(lambda x: hex[x])

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

    save_path = pathlib.Path("movies/" + movie_path.stem).absolute()
    print("Writing frames to: ", save_path)

    import os
    if save_path.exists() and save_path.is_dir():
        import glob

        list_of_files = glob.glob(str(save_path) + '/frame_*.nfp') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        i = int(''.join(filter(str.isdigit, latest_file)))
    else:
        os.makedirs(save_path)
        i = 0

    video = cv2.VideoCapture(str(movie_path))
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    for count in progressbar(range(i, num_frames), min_value=0, max_value=num_frames):
        if not video.isOpened():
            break

        ret, frame = video.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, color_space)
        shrunk = shrink_image(frame)
        nfp_image = image_to_nfp(shrunk)
        
        with open(str(save_path) + '/frame_%d.nfp' % count, 'w') as f:
            f.write(nfp_image)

    video.release()