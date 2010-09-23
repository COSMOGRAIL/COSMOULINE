#	obssl1
#	
#	Here we will apply the normalisation to the g and sig images
#	Using iraf's imarith the good old way
#	future suggestion : use pyfits ...	
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from pyraf import iraf
from variousfct import *

print "deckey :", deckey # this is a code that idendtifies this particular deconvolution.

print "You want to normalize using :", decnormfieldname

db = KirbyBase()

images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mjd']) # the \d\d* is a trick to select both 0000-like and 000-like
# we select all images that have a deckeyfilenum

print "I've selected", len(images), "images."
proquest(askquestions)

iraf.imutil()
iraf.unlearn(iraf.imutil.imarith)

for image in images:
		
	print image[deckeyfilenum], image['imgname']
	
	
	if decnormfieldname == "None":
		mycoeff = 1.0	# in this case the user *wants* to make a deconvolution without normalization.
	else :
		mycoeff = image[decnormfieldname]
		if mycoeff == None:
			print "WARNING : no coeff available, using 1.0"
			mycoeff = 1.0
	print mycoeff
	
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

notify(computer, withsound, "I've normalized the images for %s" %deckey)

