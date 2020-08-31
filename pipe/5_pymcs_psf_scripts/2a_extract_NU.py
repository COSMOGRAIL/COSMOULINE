execfile("../config.py")
 
from kirbybase import KirbyBase, KBError
from variousfct import *
import forkmap
import glob
import star


#import src.lib.utils as fn
from MCS_interface import MCS_interface

psfstars = star.readmancat(psfstarcat)


# Select images to treat
db = KirbyBase()


if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
elif update:
	print "This is an update"
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	askquestions = False
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will extract the PSF of %i images." % len(images)

ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)


for i, img in enumerate(images):
	img["execi"] = (i+1) # We do not write this into the db, it's just for this particular run.

def extractpsf(image):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	print "Image %i : %s" % (image["execi"], imgpsfdir)
	
	os.chdir(imgpsfdir)
	mcs = MCS_interface("pyMCS_psf_config.py")
	mcs.set_up_workspace(extract=True, clear=False, backup=False)
	
	
forkmap.map(extractpsf, images, n = ncorestouse)

notify(computer, withsound, "PSF extraction done for psfname %s." % (psfname))

# Now we help the user with the mask creation.
if refimgname in [img["imgname"] for img in images]:
	
	imgpsfdir = os.path.join(psfdir, refimgname)
	starfiles = sorted(glob.glob(os.path.join(imgpsfdir, "results", "star_*.fits")))
	
	
	print "The stars extracted from the reference image are available here :"
	print "\n".join(starfiles)
	print "You can now open these files with DS9 to build your mask (optional)."
	print "Don't mask cosmics, only companion stars !"
	print "Save your region files respectively here :"
	
	#starfilenames = [os.path.splitext(os.path.basename(s))[0] for s in starfiles]
	
	maskfilepaths = [os.path.join(configdir, "%s_mask_%s.reg" % (psfkey, name)) for name in [s.name for s in psfstars]]
	print "\n".join(maskfilepaths)
	
	print "If asked, use physical coordinates and DS9 (or REG) file format."
else:
	if not update:
		print "By the way, the reference image was not among these images !"
		print "You should always have the reference image in your selection."

