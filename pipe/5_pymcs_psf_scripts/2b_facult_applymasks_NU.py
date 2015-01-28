#	We look for the ds9 region files, read them, and mask corresponding regions in the sigma images.


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import cosmics # used to read and write the fits files
import ds9reg
import glob
import numpy as np
import star
psfstars = star.readmancat(psfstarcat)
# We read the region files

for i, s in enumerate(psfstars):
	print '---------------PSF STAR------------------'
	print s.name
	print '-----------------------------------------'

	
	s.filenumber = (i+1)
	possiblemaskfilepath = os.path.join(configdir, "%s_mask_%s.reg" % (psfkey, s.name))
	print 'mask file path is: ',possiblemaskfilepath
	if os.path.exists(possiblemaskfilepath):
		
		s.reg = ds9reg.regions(128, 128) # hardcoded for now # Warning, can cause a lot of trouble when dealing with images other than ECAM 
		s.reg.readds9(possiblemaskfilepath, verbose=False)
		s.reg.buildmask(verbose = False)
		
		print "You masked %i pixels of star %s." % (np.sum(s.reg.mask), s.name)
	else:
		print "No mask file for star %s." % (s.name)

proquest(askquestions)
		

# Select images to treat
db = KirbyBase()


if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])


print "Number of images to treat :", len(images)
proquest(askquestions)


for i, image in enumerate(images):
	
	print "%i : %s" % (i+1, image['imgname'])
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	os.chdir(os.path.join(imgpsfdir, "results"))
			
	for s in psfstars:
		
		if not hasattr(s, 'reg'): # If there is no mask for this star
			continue
		# We modify the sigma image
		sigfilename = "starsig_%03i.fits" % s.filenumber
		(sigarray, sigheader) = fromfits(sigfilename, verbose=False)

		sigarray[s.reg.mask] = 1.0e8
	
		tofits(sigfilename, sigarray, sigheader, verbose=False)
		print 'saved !'

print "Done."

