
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import glob


print "I will simply remove all"
print "imgname_skysub.fits"
print "imgname_sky.fits"
print "imgname.fits"
print "images from the alidir."
print 'This will save some disk space, now that images are aligned...'
print 'You can rebuild these images at any time if needed.'

# We select the images to treat :
db = KirbyBase()
images = db.select(imgdb, ['recno'], ["*"], returnType='dict', sortFields=['setname','mjd'])

nbrofimages = len(images)

for i, image in enumerate(images):
	print i+1, "/", nbrofimages, " : ", image['imgname']
	
	rmfiles = ["%s%s" % (image["imgname"], ext) for ext in [".fits", "_skysub.fits", "_sky.fits"]]
	
	for rmfile in rmfiles:
		rmpath = os.path.join(alidir, rmfile)
		if os.path.isfile(rmpath):
			print "Removing %s ..." % (rmpath)
			os.remove(rmpath)



