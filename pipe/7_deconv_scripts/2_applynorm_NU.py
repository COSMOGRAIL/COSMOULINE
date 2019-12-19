#	
#	Here we will apply the normalisation to the g and sig images
#
import sys

if len(sys.argv) == 2:
	execfile("../config.py")
	decobjname = sys.argv[1]
	deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
	ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
	decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
	deckeyfilenum = "decfilenum_" + deckey
	deckeypsfused = "decpsf_" + deckey
	deckeynormused = "decnorm_" + deckey
	decdir = os.path.join(workdir, deckey)
	print "You are running the deconvolution on all the stars at once."
	print "Current star : " + sys.argv[1]

else :
	execfile("../config.py")

from kirbybase import KirbyBase, KBError
from variousfct import *
import astropy.io.fits as pyfits

if update:
	# override config settings...
	execfile(os.path.join(configdir, 'deconv_config_update.py'))
	askquestions=False
	# nothing more. Let's run on the whole set of images now.

print "deckey : %s" % deckey # this is a code that idendtifies this particular deconvolution.
db = KirbyBase()

images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mjd']) # the \d\d* is a trick to select both 0000-like and 000-like
# we select all images that have a deckeyfilenum

# We duplicate the ref image :
refimage = [image for image in images if image['imgname'] == refimgname][0] # we take the first and only element.
images.insert(0, refimage.copy()) # This copy is important !!!
images[0][deckeyfilenum] = mcsname(1) # The duplicated ref image gets number 1

print "I've selected %i images (ref image is duplicated)." % len(images)
proquest(askquestions)

for image in images:
		
	print image[deckeyfilenum], image['imgname']
	
	mycoeff = image[deckeynormused]
	
	# First we handle g.fits :
	
	inname = os.path.join(decdir, "g" + image[deckeyfilenum] + "_notnorm.fits")
	outname = os.path.join(decdir, "g" + image[deckeyfilenum] + ".fits")
	if os.path.exists(outname):
		os.remove(outname)
	
	(a_notnorm, h) = pyfits.getdata(inname, header=True)
	# No need to take care of any transpositions here, we just multiply the array by a constant.
	a = a_notnorm * mycoeff
	# We write the result :
	hdu = pyfits.PrimaryHDU(a, h)
	hdu.writeto(outname)
	
	
	# And not sig.fits, quite similar :
	
	inname = os.path.join(decdir, "sig" + image[deckeyfilenum] + "_notnorm.fits")
	outname = os.path.join(decdir, "sig" + image[deckeyfilenum] + ".fits")
	if os.path.exists(outname):
		os.remove(outname)
	
	(a_notnorm, h) = pyfits.getdata(inname, header=True)
	a = a_notnorm / mycoeff # yep, sigma would be multiplied but this image is 1/sigma !
	# We write the result :
	hdu = pyfits.PrimaryHDU(a, h)
	hdu.writeto(outname)
	

notify(computer, withsound, "I've normalized the images for %s" %deckey)

