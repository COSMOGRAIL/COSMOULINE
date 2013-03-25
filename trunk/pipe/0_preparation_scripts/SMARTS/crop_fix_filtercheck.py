#
#	Crop FITS files to remove ugly borders (prescan and overscan etc).
#	BZERO and BSCALE get applied by pyfits (we could improve this).
#	While we are at it, you can also change the filenames.
#

import os, sys, glob, pyfits, numpy

################### CONFIGURATION ###################################################################

# ABSOLUTE PATH to where the files are and how to select them :
origpaths = sorted(glob.glob("/obs/lenses_EPFL/SMARTS/J0924/raw/extracted/*.fits")) 

# ABSOLUTE PATH to the directory where you want the croped images to be written :
destdir="/obs/lenses_EPFL/SMARTS/J0924/raw/extracted_crop_R" 


#####################################################################################################


def newpath(origpath, destdir): 	# specifies how to change the name :
					# origpath is the full path to a present file, and you have to
					# return a full path to the destination file you want.
	(dirname, filename) = os.path.split(origpath)
	#newfilename = filename.replace(":", "-")
	destpath = os.path.join(destdir, filename)
	return destpath


if not os.path.isdir(destdir):
	os.mkdir(destdir)

filterlist = []

for fitsfilepath in origpaths[::-1]:
	print os.path.split(fitsfilepath)[1]

	newfitsfilepath = newpath(fitsfilepath, destdir)
	
	#hdulist = pyfits.open(fitsfilepath,ignore_missing_end=True)
	#hdulist.info()
	
	#sys.exit()
	
	pixelarray, hdr = pyfits.getdata(fitsfilepath, header=True, ignore_missing_end=True)
	#sys.exit()
	
	filterid = hdr["CCDFLTID"].strip()
	filterlist.append(filterid)
	
	
	if hdr["CCDFLTID"].strip() != "R":
		print "Filter %s, skipping this one." % (hdr["CCDFLTID"].strip())
		continue
		#print "2_%s\tFilter %s" % (os.path.splitext(os.path.split(fitsfilepath)[1])[0], hdr["CCDFLTID"])
		
	
	pixelarray = numpy.asarray(pixelarray).transpose() # To put it in the usual ds9 orientation
	
	pixelarrayshape = pixelarray.shape
	print "Input : (%i, %i), %s, %s" % (pixelarrayshape[0], pixelarrayshape[1], hdr["BITPIX"], pixelarray.dtype.name)
	
	#pixelarray = pixelarray[96:1037, 118:1024] # This was for J0158
	
	#Strange, the RXJ1131 images are smaller, they are all 1000 by 1000, probably already cropped somehow.
	# The size of the ugly border seems to increase with time. nevertheless I'll cut the maximum here ,to make it simpler.
	#pixelarray = pixelarray[60:, 140:]
	
	#For J0924 this is again different, size of borders evolve a lot. Ah no, maybe it's the same, let's try this again :
	pixelarray = pixelarray[60:, 140:]
	
	pixelarrayshape = pixelarray.shape
	print "Ouput : (%i, %i)" % (pixelarrayshape[0], pixelarrayshape[1])
	if os.path.isfile(newfitsfilepath):
		os.remove(newfitsfilepath)
	
	#hdrcardlist = hdr.ascardlist()
	#hdr["YAMP"] = "FUBAR"
	#hdr["PIXXMIT"] = "FUBAR"
	#hdr["IRFILT"] = "FUBAR"
	#hdr.verify("fix")
	
	hdu = pyfits.PrimaryHDU(pixelarray.transpose(), hdr)
	hdu.verify("fix")
	hdu.writeto(newfitsfilepath)
	

print "Filter histo :"
filterhisto = [(f, filterlist.count(f)) for f in sorted(list(set(filterlist)))]
print "\n".join(["%s : %i" % h for h in filterhisto])


