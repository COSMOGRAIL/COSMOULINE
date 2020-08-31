
import astropy.io.fits as fits
import glob
import os
import time

rawdir = "/Users/martin/Desktop/COSMOULINE/data_raw/WG2205-3727"
files = sorted(glob.glob(os.path.join(rawdir,"*.fits")))
for img in files :
    print img
    hdu = fits.open(img, mode='update',ignore_missing_end=True)
    time.sleep(0.1)
    # hdu.verify("fix")
    # hdu.flush()
    # hdu.close()
