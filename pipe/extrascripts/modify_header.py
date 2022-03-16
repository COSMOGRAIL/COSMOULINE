
import astropy.io.fits as fits
from astropy.time import Time
import os

rawdir = "/Users/martin/Desktop/COSMOULINE/data_raw/MS1134/z/"

files = os.listdir(rawdir)
for fil in files :
    s = fil.split(".")
    mjd = float(s[-3] + "." + s[-2])
    print mjd
    hdu = fits.open(rawdir+fil, mode='update')
    header = hdu[0].header
    t = Time(mjd, format='mjd')
    t.format = "fits"
    print t.value[:-9]
    header["DATE"] = t.value[:-9]


    hdu[0].header = header
    hdu.flush()
    hdu.close()

print "TO check :"
for fil in files:
    hdu = fits.open(rawdir + fil)
    print hdu[0].header["DATE"]
