import astropy.io.fits as fits
import os
import math
import numpy as np

dir = "/Users/martin/Desktop/COSMOULINE/run/MS1134_PANSTARRS_g/psf_ab/"
fold = os.listdir(dir)

for im in fold :
    hdu = fits.open(dir + im + "/images/in.fits", mode='update')
    dat = hdu[0].data
    n1,n2 = np.shape(dat)
    for i in range(n1):
        for j in range(n2):
            if math.isnan(dat[i,j]):
                dat[i,j]=0

    hdu[0].data=dat
    hdu.flush()
    hdu.close()
