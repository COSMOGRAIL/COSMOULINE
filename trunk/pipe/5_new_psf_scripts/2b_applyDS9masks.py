#	We look for the ds9 region file, read it, and mask corresponding regions in the sigma images.


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import cosmics # used to read and write the fits files
import ds9reg


# We read the region file :
ds9regfilepath = os.path.join(configdir, psfkey + "_mask.reg")
reg = ds9reg.regions(128, 128) # hardcoded for now ...
reg.readds9(ds9regfilepath)
reg.buildmask()


# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])
print "Number of images to treat :", len(images)
proquest(askquestions)


# Remember where we are
origdir = os.getcwd()

for i, image in enumerate(images):
	
	print "%i : %s" % (i+1, image['imgname'])
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	os.chdir(imgpsfdir)
			
	# We modify the sigma image
	
	(sigarray, sigheader) = cosmics.fromfits("sig001.fits", verbose=False)
	
	sigarray[reg.mask] = 1.0e-8 # yes, for the new psf it's inverted
	
	cosmics.tofits("sig001.fits", sigarray, sigheader, verbose=False)
	
	# We are done, and go back home.
	os.chdir(origdir)



print "Done."
	
	
