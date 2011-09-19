#
#	Using pyfits, we will replace the zeroes in the sigma files prior to the psf construction
#	superfast, superclean...
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import pyfits

	# remember where we are
origdir = os.getcwd()

	# select images to treat (in principle psfkeyflag alone is sufficient of course -- 
	# but just in case you put gogogo to false for an image since the extraction...)
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will treat %i images." % len(images)
proquest(askquestions)


def isNaN(x):
	return x!=x
	
def replaceNaN(filename, value):
	sigstars = pyfits.open(filename, mode='update')
	scidata = sigstars[0].data
	if True in isNaN(scidata):
		print "Yep, some work for me : ", len(scidata[isNaN(scidata)]), "pixels."
	scidata[isNaN(scidata)] = value
	sigstars.flush()
	
for n, image in enumerate(images):

	print n+1, "/", len(images), ":", image['imgname']
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	
	os.chdir(imgpsfdir)
	
	replaceNaN("sig001.fits", 1.0e-6)
	#replaceNaN("sig.fits", 1.0e-6)

	os.chdir(origdir)
	
notify(computer, withsound, "I've corrected problematic sigma images.")
	
	
