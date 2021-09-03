#
# script to imcopy (with crop and flip) the previously reduced images.
#



import os
import sys
from pyraf import iraf
from glob import glob


nowdir = "/home/epfl/tewes/DECONV/J1001/Mer2prered_notyetfliped/"
destdir = "/home/epfl/tewes/DECONV/J1001/Mer2prered/"

#nowdir = "/Users/mtewes/obs/home/epfl//ildar/SWISS_2008/J1001_mer_old/bias_flat_cor/"
#destdir = "/Users/mtewes/obs/home/epfl/tewes/DECONV/J1001/prered/"



#region = "[50:1999,50:1999]"
region = ""
rotation = "[*,-*]"
flip = "[*,-*]"


if not os.path.isdir(destdir):
	print("Make destdir !")
	sys.exit()


os.chdir(nowdir)
filelist = sorted(glob("*.fits"))

print(len(filelist), "images found.")


iraf.imutil()
iraf.unlearn(iraf.imutil.imcopy)
iraf.imgeom()
iraf.unlearn(iraf.imgeom.imtranspose)

for i, fitsfile in enumerate(filelist):

	print(i+1, fitsfile)
	imgname = fitsfile.split(".")[0]
	#iraf.imutil.imcopy(fitsfile+region, destdir+imgname+"_crop.fits")
	#iraf.imutil.imcopy(destdir+imgname+"_crop.fits"+rotation, destdir+imgname+"_flip.fits")
	
	# just a flip, no rotation (faster)
	iraf.imutil.imcopy(fitsfile+flip, destdir+imgname+".fits")
	
	# flip and rotation (to get Mercator -> Sky)
	#iraf.imutil.imcopy(fitsfile+flip, destdir+imgname+"_flip.fits")
	#iraf.imgeom.imtranspose(destdir+imgname+"_flip.fits"+rotation, destdir+imgname+".fits")

#
#	SOME EXPLANATIONS :
#
#	to rotate (i.e. transpose) an image in IRAF, you write :
#	imtranspose in.fits[*,-*] out.fits
#
#	and to flip (i.e. miror) an image, you write :
#	imcopy in.fits[*,-*] out.fits
#




	
	
