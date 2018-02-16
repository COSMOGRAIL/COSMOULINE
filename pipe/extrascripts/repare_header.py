import pyfits
import math
import astropy.io.fits as fits


img="/Users/martin/Desktop/COSMOULINE/run/J1029_HOLI/refimg_skysub.fits"
hdu = fits.open(img, mode='update',ignore_missing_end=True)
hdu.verify("fix")
hdu.flush()
hdu.close()
