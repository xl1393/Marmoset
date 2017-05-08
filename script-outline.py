from os import listdir
from os.path import isfile, join
import h5py
import cv2
import numpy as np
from skimage.util import view_as_blocks
from multiprocessing import Pool


def Down_Sample(image, block_size, func=np.sum, cval=0):

    if len(block_size) != image.ndim:
        raise ValueError("`block_size` must have the same length "
                         "as `image.shape`.")

    pad_width = []
    for i in range(len(block_size)):
        if block_size[i] < 1:
            raise ValueError("Down-sampling factors must be >= 1. Use "
                             "`skimage.transform.resize` to up-sample an "
                             "image.")
        if image.shape[i] % block_size[i] != 0:
            after_width = block_size[i] - (image.shape[i] % block_size[i])
        else:
            after_width = 0
        pad_width.append((0, after_width))

    image = np.pad(image, pad_width=pad_width, mode='constant',
                   constant_values=cval)

    out = view_as_blocks(image, block_size)

    for i in range(len(out.shape) // 2):
        out = func(out, axis=-1)

    return out

def RmIsolated_pixel(img):

    sat = np.pad(img, pad_width=1, mode='constant', constant_values=0)
    sat = np.cumsum(np.cumsum(sat, axis=0), axis=1)
    sat = np.pad(sat, ((1, 0), (1, 0)), mode='constant', constant_values=0)
    # These are all the possible overlapping 3x3 windows sums
    sum3x3 = sat[3:, 3:] + sat[:-3, :-3] - sat[3:, :-3] - sat[:-3, 3:]
    # This takes away the central pixel value
    sum3x3 -= img
    # This zeros all the isolated pixels
    img[sum3x3 == 0] = 0

    return img

def FileProcess(filename):

    print 'processing '+filename
    data=h5py.File(filename)
    img=np.asarray(data['savedata'])
    img=img.T
    #img=img[:,:,1] #take only green channel
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img=img*255 #make the graph binary(0 or 255)

    img=RmIsolated_pixel(img)
    
    for i in range(0,3):
        img=Down_Sample(img,block_size=(2,2),func=np.sum)
        
    img=img*255 #make sure the graph is binary(0 or 255)
    cv2.imwrite(filename.split('.')[0]+'-outline.jpg',img)

    print 'finish '+filename


if __name__ == "__main__":
    filepath='m820F/fluorooutline/'
    filelist = [filepath + f for f in listdir(filepath) if isfile(join(filepath, f))]
    
    p=Pool(2)
    p.map(FileProcess,tuple(filelist))