import numpy as np
import os

execfile("../config.py")
import ds9reg
from variousfct import *

#This script is made to mask part of the background to avoid influencing the fit


filename = 'back0001'
outputname = 'back_m'
extension = ".fits"
back = os.path.join(decdir,filename+extension)
inverted = True

region = os.path.join(configdir,deckey + '_mask_lens.reg')

print 'mask file path is: ', os.path.join(configdir,deckey + '_mask_lens.reg')
if os.path.exists(region):

    reg = ds9reg.regions(128,128)  # hardcoded for now # Warning, can cause a lot of trouble when dealing with images other than ECAM
    reg.readds9(region, verbose=True)
    reg.buildmask(verbose=False)

    (backarray, backheader) = fromfits(back, verbose=False)

    backarray[reg.mask] = 0.0

    tofits(os.path.join(decdir,outputname + extension), backarray, backheader, verbose=False)

    print "You masked %i pixels of the background" %np.sum(reg.mask)
    print 'saved !'
else:
    print "No mask file"



