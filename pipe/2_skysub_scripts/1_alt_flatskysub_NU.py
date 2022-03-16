#
#	We subtract a flat value (skylevel from the database)	
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import shutil
import os
import numpy as np


db = KirbyBase()
if thisisatest:
	print "This is a test run."
	images = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict')
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')
	
	
nbrimages = len(images)
print "Number of images to treat :", nbrimages
proquest(askquestions)

starttime = datetime.now()

for i,image in enumerate(images):
	
	print "+ " * 30
	print "%5i/%i : %s" % (i+1, nbrimages, image["imgname"])
	
	imagepath = os.path.join(alidir, image["imgname"] + ".fits")
	
	skylevel = image["skylevel"]
	print "Skylevel to be subtracted : %.3f" % skylevel
	
	(imagea, imageh) = fromfits(os.path.join(alidir, image["imgname"] + ".fits"), verbose = False)
	skya = np.ones(imagea.shape) * skylevel
	
	skysubimagea = imagea - skya
	
	skysubimagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
	if os.path.isfile(skysubimagepath):
		os.remove(skysubimagepath)
	
	
	skyimagepath = os.path.join(alidir,  image["imgname"] + "_sky.fits")
	if os.path.isfile(skyimagepath):
		os.remove(skyimagepath)
	
	
	tofits(skysubimagepath, skysubimagea, hdr = imageh, verbose = True)
	tofits(skyimagepath, skya, hdr = None, verbose = True)
	
	
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "The sky is no longer the limit. I took %s" % timetaken)


