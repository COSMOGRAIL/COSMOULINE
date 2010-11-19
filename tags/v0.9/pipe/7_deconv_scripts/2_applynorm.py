#	
#	Here we will apply the normalisation to the g and sig images
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import pyfits

print "deckey : %s" % deckey # this is a code that idendtifies this particular deconvolution.
db = KirbyBase()

images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mjd']) # the \d\d* is a trick to select both 0000-like and 000-like
# we select all images that have a deckeyfilenum

print "I've selected", len(images), "images."
proquest(askquestions)

# No longer used :
#iraf.imutil()
#iraf.unlearn(iraf.imutil.imarith)

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
	
	
	# The old way, using pyraf :
	"""
	inname = decdir + "g" + image[deckeyfilenum] + "_notnorm.fits"
	outname = decdir + "g" + image[deckeyfilenum] + ".fits"
	if os.path.isfile(outname):
		os.remove(outname)
	iraf.imutil.imarith(operand1=inname, op="*", operand2=mycoeff, result=outname)

	inname = decdir + "sig" + image[deckeyfilenum] + "_notnorm.fits"
	outname = decdir + "sig" + image[deckeyfilenum] + ".fits"
	if os.path.isfile(outname):
		os.remove(outname)
	iraf.imutil.imarith(operand1=inname, op="/", operand2=mycoeff, result=outname)
	# yep, sigma would be multiplied but this image is 1/sigma !
	"""

notify(computer, withsound, "I've normalized the images for %s" %deckey)

