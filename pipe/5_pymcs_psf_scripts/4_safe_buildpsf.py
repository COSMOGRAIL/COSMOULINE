execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import forkmap

import MCS_src.lib.utils as fn
from MCS_interface import MCS_interface


# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])


print "I will build the PSF of %i images." % len(images)

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)

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

