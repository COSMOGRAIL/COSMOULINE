#
#	Crop FITS files to remove ugly borders (prescan and overscan etc).
#	BZERO and BSCALE get applied by pyfits (we could improve this).
#	While we are at it, you can also change the filenames.
#

import os, sys, glob, pyfits, numpy

################### CONFIGURATION ###################################################################

# ABSOLUTE PATH to where the files are and how to select them :
origpaths = sorted(glob.glob("/Volumes/Saturn/Cloverleaf/Orig_liverpool_images/*.fits")) 

# ABSOLUTE PATH to the directory where you want the croped images to be written :
destdir="/Volumes/Saturn/Cloverleaf/Crop_liverpool_images" 

def newpath(origpath, destdir): 	# specifies how to change the name :
					# origpath is the full path to a present file, and you have to
					# return a full path to the destination file you want.
	
	(dirname, filename) = os.path.split(origpath)
	newfilename = filename.replace(":", "-")
	destpath = os.path.join(destdir, newfilename)
	return destpath

# pixels you want to keep (numpy style) :
region = "[15:1015, 15:1015]"
#region = None # If you do not want to crop

#####################################################################################################



if not os.path.isdir(destdir):
	os.mkdir(destdir)


for fitsfilepath in origpaths:
	print os.path.split(fitsfilepath)[1]

	newfitsfilepath = newpath(fitsfilepath, destdir)
	
	pixelarray, hdr = pyfits.getdata(fitsfilepath, header=True)
	pixelarray = numpy.asarray(pixelarray).transpose() # To put it in the usual ds9 orientation
	
	pixelarrayshape = pixelarray.shape
	print "Input : (%i, %i), %s, %s" % (pixelarrayshape[0], pixelarrayshape[1], hdr["BITPIX"], pixelarray.dtype.name)
	
	
	if region != None:
		exec("pixelarray = pixelarray%s" % (region))
	
	pixelarrayshape = pixelarray.shape
	print "Ouput : (%i, %i)" % (pixelarrayshape[0], pixelarrayshape[1])
	if os.path.isfile(newfitsfilepath):
		os.remove(newfitsfilepath)
	
	
	hdu = pyfits.PrimaryHDU(pixelarray.transpose(), hdr)
	hdu.writeto(newfitsfilepath)