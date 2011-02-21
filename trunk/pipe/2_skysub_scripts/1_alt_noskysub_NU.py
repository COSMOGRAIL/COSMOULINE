#
#	mimics the sky subtraction without doing anything to the images
#	we do a copy, as this is the first time we need the actual images.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

nbrimages = len(images)

print "I will not change the images, just (link or) copy the files."
print "uselinks : %s" % (uselinks)
proquest(askquestions)

print "Number of images to treat :", nbrimages
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):
	print i+1, "/", nbrimages, ":", justname
	
	recno = image['recno']
	justname = image['imgname']
	withskyfilepath = os.path.join(alidir, image['imgname'] + ".fits")
	
	noskyfilepath = os.path.join(alidir, image['imgname'] + "_skysub.fits")
	
	copyorlink(withskyfilepath, noskyfilepath, uselinks = uselinks)
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)
notify(computer, withsound, "Files copyorlinked. It took %s" % timetaken)


