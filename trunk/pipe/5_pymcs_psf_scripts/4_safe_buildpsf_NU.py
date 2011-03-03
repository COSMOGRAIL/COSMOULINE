execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import forkmap
import star

import src.lib.utils as fn
from MCS_interface import MCS_interface

####
nofitnum = True

####
# Select images to treat
db = KirbyBase()

if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will build the PSF of %i images." % len(images)

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)


psfstars = star.readmancat(psfstarcat)  # this is only used if nofitnum
print "We have %i stars" % (len(psfstars))
#for star in psfstars:
#	print star.name

errorimglist = []

for i, img in enumerate(images):
	img["execi"] = (i+1) # We do not write this into the db, it's just for this particular run.

def buildpsf(image):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	print "Image %i : %s" % (image["execi"], imgpsfdir)
	
	os.chdir(imgpsfdir)
	
	mcs = MCS_interface("pyMCS_psf_config.py")
	
	try:	
		print "I'll try this one."
		mcs.fitmof()
		if nofitnum:
			mcs.psf_gen()
			# Then we need to write some additional files, to avoid png crash
			empty128 = np.zeros((128, 128))
			tofits("results/psfnum.fits", empty128)
			empty64 = np.zeros((64, 64))
			for i in range(len(psfstars)):
				tofits("results/difnum%02i.fits" % (i+1), empty64)
			
		else:
			mcs.fitnum()
		
	except (IndexError):
		print "WTF, an IndexError ! "
		errorimglist.append(image)
		
	else:
		print "It worked !"
	
	psffilepath = os.path.join(imgpsfdir, "s001.fits")
	if os.path.exists(psffilepath):
		os.remove(psffilepath)
	os.symlink(os.path.join(imgpsfdir, "results", "s_1.fits"), psffilepath)
	
	
starttime = datetime.now()
forkmap.map(buildpsf, images, n = ncorestouse)
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

if os.path.isfile(psfkicklist):
	print "The psfkicklist already exists :"
else:
	cmd = "touch " + psfkicklist
	os.system(cmd)
	print "I have just touched the psfkicklist for you :"
print psfkicklist

if len(errorimglist) != 0:
	print "pyMCS raised an IndexError on the following images :"
	print "(Add them to the psfkicklist, retry them with a testlist, ...)"
	print "\n".join(["%s\t%s" % (image['imgname'], "pyMCS IndexError") for image in errorimglist])
else:
	print "I could build the PSF of all images."

notify(computer, withsound, "PSF construction for psfname: %s using %i cores. It took me %s ." % (psfname, ncorestouse, timetaken))

