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


for i, img in enumerate(images):
	img["execi"] = i # We do not write this into the db, it's just for this particular run.

def buildpsf(image):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	print "Image %i : %s" % (image["execi"], imgpsfdir)
	
	os.chdir(imgpsfdir)
	
	mcs = MCS_interface("pyMCS_psf_config.py")
	
	mcs.set_up_workspace(extract=True, clear=False, backup=False)
	mcs.fitmof()
	mcs.fitnum()
	
	os.symlink(os.path.join(imgpsfdir, "results", "s_1.fits"), os.path.join(imgpsfdir, "s001.fits"))
	
	
starttime = datetime.now()
forkmap.map(buildpsf, images, n = ncorestouse)
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "PSF construction for psfname: %s using %i cores. It took me %s ." % (psfname, ncorestouse, timetaken))

