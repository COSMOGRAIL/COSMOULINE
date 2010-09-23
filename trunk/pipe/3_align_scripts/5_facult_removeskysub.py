
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import glob

# We select the images to treat :
db = KirbyBase()

print 'I will simply remove all "*_skysub.fits" images from the alidir.'
print 'This will save some disk space, now that images are aligned...'
print 'You can rebuild the skysub images at any time if needed.'


skysubpaths = glob.glob(os.path.join(alidir, "*_skysub.fits"))
print "I would delete %i files." % len(skysubpaths)

proquest(askquestions)

for i, skysubpath in enumerate(skysubpaths):
	print i
	#print skysubpath
	os.remove(skysubpath)
	
	

