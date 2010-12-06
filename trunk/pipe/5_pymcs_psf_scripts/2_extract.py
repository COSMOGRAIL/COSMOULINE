execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import forkmap

import MCS_src.lib.utils as fn
from MCS_interface import MCS_interface

# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will extract the PSF of %i images." % len(images)

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)


for i, img in enumerate(images):
	img["execi"] = i # We do not write this into the db, it's just for this particular run.

def extractpsf(image):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	print "Image %i : %s" % (image["execi"], imgpsfdir)
	
	os.chdir(imgpsfdir)
	mcs = MCS_interface("pyMCS_psf_config.py")
	mcs.set_up_workspace(extract=True, clear=False, backup=False)
	
	
forkmap.map(extractpsf, images, n = ncorestouse)

notify(computer, withsound, "PSF extraction done for psfname %s." % (psfname))

