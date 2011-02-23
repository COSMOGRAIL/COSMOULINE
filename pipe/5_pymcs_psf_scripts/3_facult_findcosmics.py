"""
We use cosmics.py to locate cosmics in the extracted images.
We do not clean them, but mask them in the corresponding sigma images.
We do not update the database.
"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import forkmap
import cosmics
import star
#import numpy as np

###########

sigclip = cosmicssigclip
sigfrac = 0.3
objlim = 1.0

###########

# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will find cosmics of %i images." % len(images)

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)

for i, img in enumerate(images):
	img["execi"] = (i+1) # We do not write this into the db, it's just for this particular run.

# We see how many stars we have :
psfstars = star.readmancat(psfstarcat)


def findcosmics(image):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	print "Image %i : %s" % (image["execi"], imgpsfdir)
	
	os.chdir(os.path.join(imgpsfdir, "results"))
	
	pssl = image['skylevel']
	gain = image['gain']
	readnoise = image['readnoise']
	print "Gain %.2f, PSSL %.2f, Readnoise %.2f" % (gain, pssl, readnoise)

	for i in range(len(psfstars)):
		starfilename = "star_%03i.fits" % (i+1)
		sigfilename = "starsig_%03i.fits" % (i+1)
		origsigfilename = "origstarsig_%03i.fits" % (i+1)
		starmaskfilename = "starmask_%03i.fits" % (i+1)
		starcosmicspklfilename = "starcosmics_%03i.pkl" % (i+1)
	
		# We reset everyting
		if os.path.isfile(origsigfilename):
			# Then we reset the original sigma image :
			if os.path.isfile(sigfilename):
				os.remove(sigfilename)
			os.rename(origsigfilename, sigfilename)
			
		if os.path.isfile(starmaskfilename):
			os.remove(starmaskfilename)
		if os.path.isfile(starcosmicspklfilename):
			os.remove(starcosmicspklfilename)
	
		# We read array and header of that fits file :
		(a, h) = cosmics.fromfits(starfilename, verbose=False)
	
		# Creating the object :
		c = cosmics.cosmicsimage(a, pssl=pssl, gain=gain, readnoise=readnoise, sigclip=sigclip, sigfrac=sigfrac, objlim=objlim, satlevel=-1.0, verbose=False)
	
		#print pssl, gain, readnoise, sigclip, sigfrac, objlim
		
		c.run(maxiter=3)
	
		ncosmics = np.sum(c.mask)
		#print ncosmics
		#if ncosmics != 0:
		#	print "--- %i pixels ---" % ncosmics
		
		# We write the mask :
		cosmics.tofits(starmaskfilename, c.getdilatedmask(size=5), verbose=False)
		
		# And the labels (for later png display) :
		cosmicslist = c.labelmask()
		writepickle(cosmicslist, starcosmicspklfilename, verbose=False)
		
		# We modify the sigma image, but keep a copy of the original :
		os.rename(sigfilename, origsigfilename)
		(sigarray, sigheader) = cosmics.fromfits(origsigfilename, verbose=False)
		sigarray[c.getdilatedmask(size=5)] = 1.0e8
		cosmics.tofits(sigfilename, sigarray, sigheader, verbose=False)
	
	
forkmap.map(findcosmics, images, n = ncorestouse)

notify(computer, withsound, "Cosmics masked for psfname %s." % (psfname))
