#
#	Crop FITS files to remove ugly borders (prescan and overscan etc).
#	BZERO and BSCALE get applied by pyfits (we could improve this).
#	While we are at it, you can also change the filenames.
#	New : create png images of the cropped fits
#
#
execfile("../../config.py")
import os, sys, glob, pyfits, numpy
from variousfct import *
import f2n
################### CONFIGURATION ###################################################################

# ABSOLUTE PATH to where the files are and how to select them :
origpaths = sorted(glob.glob(os.path.join(rawdir,'*')))
origpaths = [p for p in origpaths if os.path.isfile(p)]

# ABSOLUTE PATH to the directory where you want the croped images to be written :
destdir=os.path.join(rawdir,'cropped')
if not os.path.exists(destdir):
	os.mkdir(destdir)

# croped images png path :
pngdir=os.path.join(rawdir,'cropped_png')
if not os.path.exists(pngdir):
	os.mkdir(pngdir)

#####################################################################################################


def newpath(origpath, destdir): 	# specifies how to change the name :
					# origpath is the full path to a present file, and you have to
					# return a full path to the destination file you want.
	(dirname, filename) = os.path.split(origpath)
	#newfilename = filename.replace(":", "-") # bwahaha, mac, bwahahahaha. Noob.
	destpath = os.path.join(destdir, filename)
	return destpath


filterlist = []

for fitsfilepath in origpaths[::-1]:
	print os.path.split(fitsfilepath)[1]

	newfitsfilepath = newpath(fitsfilepath, destdir)
	
	#hdulist = pyfits.open(fitsfilepath,ignore_missing_end=True)
	#hdulist.info()
	
	#sys.exit()
	pixelarray, hdr = pyfits.getdata(fitsfilepath, header=True, ignore_missing_end=True)
	#sys.exit()
	
	# I commented this for the HE0435 SMARTS data...as the header is not the same...
		
	filterid = hdr["CCDFLTID"].strip()
	filterlist.append(filterid)
	
	"""
	if hdr["CCDFLTID"].strip() != "R":
		print "Filter %s, skipping this one." % (hdr["CCDFLTID"].strip())
		continue
		#print "2_%s\tFilter %s" % (os.path.splitext(os.path.split(fitsfilepath)[1])[0], hdr["CCDFLTID"])
	"""
		
	
	pixelarray = numpy.asarray(pixelarray).transpose() # To put it in the usual ds9 orientation
	pixelarrayshape = pixelarray.shape
	print "Input : (%i, %i), %s, %s" % (pixelarrayshape[0], pixelarrayshape[1], hdr["BITPIX"], pixelarray.dtype.name)
	
	#pixelarray = pixelarray[96:1037, 118:1024] # This was for J0158
	
	#Strange, the RXJ1131 images are smaller, they are all 1000 by 1000, probably already cropped somehow.
	# The size of the ugly border seems to increase with time. nevertheless I'll cut the maximum here ,to make it simpler.
	#pixelarray = pixelarray[60:, 140:]
	
	#For J0924 and WFI2033 this is again different, size of borders evolve a lot. Ah no, maybe it's the same, let's try this again. A few images are ugly anyway, might want to redo it a some point... :
	#pixelarray = pixelarray[60:, 140:]
	
	#For HE0435 some images are really ugly..., with enormous borders...
	# pixelarray = pixelarray[170:950, 404:950]
	pixelarray = pixelarray[77:950, 156:950] #for WFI2026

	
	
	
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

########
print "\n Now I make pngs of these croped images vs raw images"
proquest(askquestions)

if not os.path.isdir(pngdir):
	os.mkdir(pngdir)

croppaths = os.popen('ls '+destdir)
croppaths = [os.path.join(destdir,croppath).split('\n')[0] for croppath in croppaths]


for origpath, croppath in zip(origpaths,croppaths):

	
	cropimage = f2n.fromfits(croppath)
	cropimage.setzscale("auto", "auto")
	cropimage.makepilimage(scale = 'log', negative = False)
	
	pngpath   = os.path.join(pngdir,os.path.basename(croppath)).split('.fits')[0]+'.png'
	cropimage.tonet(pngpath)

