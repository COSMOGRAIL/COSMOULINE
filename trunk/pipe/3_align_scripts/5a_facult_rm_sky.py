
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import glob

# We select the images to treat :
db = KirbyBase()

print 'I will simply remove all "*_skysub.fits" and "*_sky.fits" images from the alidir.'
print 'This will save some disk space, now that images are aligned...'
print 'You can rebuild the skysub images at any time if needed.'

skysubpaths = glob.glob(os.path.join(alidir, "*_skysub.fits"))
skypaths = glob.glob(os.path.join(alidir, "*_sky.fits"))
print "I would delete %i + %i files." % (len(skysubpaths), len(skypaths))

proquest(askquestions)

for i, filepath in enumerate(skysubpaths + skypaths):
	print "%i : %s" % (i+1, filepath)
	os.remove(filepath)
	
print "Done."
	

