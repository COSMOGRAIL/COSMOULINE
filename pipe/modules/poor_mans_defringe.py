#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 17:25:02 2022

@author: fred dux


This is a defringer based on sextractor, basic inpainting of a binned
image and interpolation. 
Its purpose is to (try and) rescue data obtained without dithering.
(the canonical way of defringing is taking the median of dithered images.)

"""
import os
from   subprocess        import  call
import numpy             as      np
import cv2
from   time              import  time
from   scipy.ndimage     import  binary_dilation
from   astropy.io        import  fits

from skimage.transform   import  resize
from scipy.ndimage       import  median_filter


def binning(data, n=256):
    #returns an array of shape (n,n)
    bs = data.shape[0]//n,data.shape[1]//n  # blocksize averaged over
    return np.reshape(np.array([np.nanmean(data[k1*bs[0]:(k1+1)*bs[0],k2*bs[1]:(k2+1)*bs[1]]) 
                                for k1 in range(n) for k2 in range(n)]),(n,n))


def runSextractor(imagepath):
    # run sextractor and obtain a segmentation map and a catalogue.
    catfile = imagepath.replace(".fits", '.catfile.txt')
    segmap  = imagepath.replace('.fits', '.segmap.fits')
    options = ['sex', str(imagepath), 
               '-CHECKIMAGE_TYPE', 'SEGMENTATION', '-CHECKIMAGE_NAME', str(segmap),
               '-CATALOG_NAME', str(catfile)]
    
    call(options)
    return segmap, catfile


def getMask(segmap, catfile):
    mask = fits.getdata(segmap)
    starid, elongation = np.loadtxt(catfile, usecols=(0, 18), unpack=1)
    for star, el in zip(starid, elongation):
        if el > 4:
            mask[mask==star] = 0
    mask[mask!=0] = 1
    maska         = binary_dilation(mask, iterations=20)
    mask          = np.where(maska)
    return maska, mask


def estimateFringes(imagepath):
    # run sextractor, find all the sources and mask them.
    segmap, catfile = runSextractor(imagepath)
    maska, mask     = getMask(segmap, catfile)

    fringed       = fits.getdata(imagepath)
    originalshape = fringed.shape
    fringed       = median_filter(fringed, 3)
    # mask the stars:
    fringed[mask] = np.nan
    
    
    binned = binning(fringed.copy(), 256)
    binned = median_filter(binned, 2)
    maskabinned = np.isnan(binned)
    maskabinned = maskabinned.astype(np.uint8)
    
    
    dst_TELEA = cv2.inpaint(binned, maskabinned, 3, cv2.INPAINT_TELEA)
    
    fringes = resize(dst_TELEA, originalshape)
    
    os.remove(segmap)
    os.remove(catfile)
    
    return fringes


if __name__ == "__main__":
    
    fringed = "/run/media/fred/backup_storage/LCO_second_pass_reductions/J2305+3714/DATA/ali/ip_ogg2m001-ep03-20211026-0074-e91_skysub.fits"
    fringed = "/run/media/fred/backup_storage/LCO_second_pass_reductions/J2305+3714/DATA/ali/zs_ogg2m001-ep05-20211029-0107-e91_skysub.fits"
    t0 = time()
    fringes   = estimateFringes(fringed)
    moriginal = fits.getdata(fringed) 
    defringed = moriginal - fringes
    print(f"Took {time()-t0} to defringe {fringed}.")
       #%%
    vmino, vmaxo = np.percentile(moriginal, (2,99.5))
    import matplotlib.pyplot as plt
    plt.subplot(131)
    plt.title('original')
    plt.imshow(moriginal,vmin=vmino,vmax=vmaxo)
    plt.xticks([]); plt.yticks([])
    plt.subplot(132)
    plt.imshow(fringes, vmin=vmino, vmax=vmaxo)
    plt.xticks([]); plt.yticks([])
    plt.title('fringes')
    plt.subplot(133)
    plt.imshow(defringed, vmin=vmino, vmax=vmaxo)
    plt.title('subtraction')
    plt.xticks([]); plt.yticks([])
    
    plt.tight_layout()
