import astropy.io.fits as pf
import scipy.misc as sc
import numpy as np
execfile("../config.py")

filename = "/obj_lens_ref_input.fits"
data = pf.open(workdir+filename)[0].data

sc.imsave(workdir + filename[:-4] + ".png", data)