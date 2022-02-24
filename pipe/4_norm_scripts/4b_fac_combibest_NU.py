#
#	second part, we do the combination
#
#	this scripts liked to crash if there are too many images selected...
#	then, on a particularly bright day i discovered that it works if
#	you use just combine or flatcombine etc instead of imcombine !!!
#
#	in fact this is not true, it still crashes if combining many images.
#	Viva iraf...
#
import numpy as np
import shutil
from astropy.io import fits
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import settings, combibestkey, imgdb
from modules.variousfct import proquest, mterror
from modules.kirbybase import KirbyBase
db = KirbyBase()


askquestions = settings['askquestions']
combibestname = settings['combibestname']
workdir = settings['workdir']


print(("combibestname : %s" % combibestname))
proquest(askquestions)

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])

for setname in usedsetnames:
    print(f"Making image for band {setname}")
    combidir = os.path.join(workdir, f"{setname}_{combibestkey}")
    
    
    
    if not os.path.isdir(combidir):
    	raise mterror("I cannot find the images ... check the combination name !")
    
    os.chdir(combidir)
    
    
    outputname = f"{setname}_{combibestkey}.fits"
    if os.path.isfile(outputname):
    	os.remove(outputname)
    
    
    combinearray = []
    with open('irafinput.txt', 'r') as f:
        for line in f.readlines():
            combinearray.append(fits.getdata(line.strip()))
    combinearray = np.array(combinearray)
    resultimage = np.median(combinearray, axis=0)
    fits.writeto(outputname, resultimage, overwrite=1)
        
    # iraf.images.immatch.imcombine("@irafinput.txt", output = outputname)
    
    shutil.move(outputname, "../.")

print("Done.")


###############################################################################
############################### old iraf parameters ########################### 
###############################################################################
# iraf.unlearn(iraf.images.immatch.imcombine)
# iraf.images.immatch.imcombine.combine = "median"

# For your info, the default parameters are :
"""
input   =                       List of images to combine
output  =                       List of output images
(headers=                     ) List of header files (optional)
(bpmasks=                     ) List of bad pixel masks (optional)
(rejmask=                     ) List of rejection masks (optional)
(nrejmas=                     ) List of number rejected masks (optional)
(expmask=                     ) List of exposure masks (optional)
(sigmas =                     ) List of sigma images (optional)
(logfile=               STDOUT) Log file

(combine=              average) Type of combine operation
(reject =                 none) Type of rejection
(project=                   no) Project highest dimension of input images?
(outtype=                 real) Output image pixel datatype
(outlimi=                     ) Output limits (x1 x2 y1 y2 ...)
(offsets=                 none) Input image offsets
(masktyp=                 none) Mask type
(maskval=                    0) Mask value
(blank  =                   0.) Value if there are no pixels

(scale  =                 none) Image scaling
(zero   =                 none) Image zero point offset
(weight =                 none) Image weights
(statsec=                     ) Image section for computing statistics
(expname=                     ) Image header exposure time keyword

(lthresh=                INDEF) Lower threshold
(hthresh=                INDEF) Upper threshold
(nlow   =                    1) minmax: Number of low pixels to reject
(nhigh  =                    1) minmax: Number of high pixels to reject
(nkeep  =                    1) Minimum to keep (pos) or maximum to reject (neg)
(mclip  =                  yes) Use median in sigma clipping algorithms?
(lsigma =                   3.) Lower sigma clipping factor
(hsigma =                   3.) Upper sigma clipping factor
(rdnoise=                   0.) ccdclip: CCD readout noise (electrons)
(gain   =                   1.) ccdclip: CCD gain (electrons/DN)
(snoise =                   0.) ccdclip: Sensitivity noise (fraction)
(sigscal=                  0.1) Tolerance for sigma clipping scaling corrections
(pclip  =                 -0.5) pclip: Percentile clipping parameter
(grow   =                   0.) Radius (pixels) for neighbor rejection
(mode   =                   ql)
"""
###############################################################################
###############################################################################
###############################################################################

