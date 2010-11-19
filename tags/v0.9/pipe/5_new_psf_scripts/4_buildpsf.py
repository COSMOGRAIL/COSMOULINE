#
#	We launch the PSF construction in one directory after the other.
#	Very easy now that everything is ready.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta

# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])


# Remember where we are.
origdir = os.getcwd()

print "I will treat %i images." % len(images)
proquest(askquestions)

starttime = datetime.now()
for n, image in enumerate(images):
	print "- " * 40
	print n+1, "/", len(images), ":", image['imgname']
	notify(computer, withsound, "Number %i, out of %i." %(n+1, len(images)))

	imgpsfdir = os.path.join(psfdir, image['imgname'])

	os.chdir(imgpsfdir)
	os.system(psfexe)
	os.chdir(origdir)
	
	
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

print "I'm done with the PSF construction for psfname: %s" % psfname
notify(computer, withsound, "Youpie, that's it. It took me %s ." % timetaken)
