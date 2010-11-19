#
# mini-script to imcopy (with crop) some images.
#



import os
import sys
from pyraf import iraf
from glob import glob


nowdir = "/Volumes/Saturn/Cloverleaf/Orig_liverpool_images/"
destdir = "/Volumes/Saturn/Cloverleaf/Crop_liverpool_images/"

region = "[15:1014,14:1015]"


if not os.path.isdir(destdir):
	print "Make destdir !"
	sys.exit()


os.chdir(nowdir)
filelist = sorted(glob("*.fits"))

print len(filelist), "images found."

iraf.imutil()
iraf.unlearn(iraf.imutil.imcopy)
iraf.imgeom()
iraf.unlearn(iraf.imgeom.imtranspose)

for i, fitsfile in enumerate(filelist):

	print i+1, fitsfile
	imgname = os.path.splitext(fitsfile)[0]
	
	#iraf.imutil.imcopy(fitsfile+region, destdir+imgname+"_crop.fits")
	iraf.imutil.imcopy(fitsfile+region, destdir+"CR"+imgname+".fits")
	
