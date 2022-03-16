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

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from pyraf import iraf
from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *
import time


print("combibestname : %s" % combibestname)
proquest(askquestions)


combidir = os.path.join(workdir, combibestkey)



if not os.path.isdir(combidir):
	raise mterror("I cannot find the images ... check the combination name !")
	
	
iraf.unlearn(iraf.images.immatch.imcombine)
iraf.images.immatch.imcombine.combine = "median"

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

os.chdir(combidir)


outputname = "%s.fits" % combibestkey
if os.path.isfile(outputname):
	os.remove(outputname)


iraf.images.immatch.imcombine("@irafinput.txt", output = outputname)

shutil.move(outputname, "../.")

print("Done.")



