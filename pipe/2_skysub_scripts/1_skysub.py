#
#	subtracts the sky from the images, using sextractor
#	We save the sky image into a file, then subtract it.
#	This has a large footprint on diskspace, but you can delete some afterwards.
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import shutil
import os


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
	
	# We run sextractor  on the image in electrons :
	os.system("%s %s -c default_sky_template.sex -CATALOG_TYPE NONE -GAIN %.3f -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f" % (sex, imagepath, image["gain"], image["pixsize"], image["satur_level"]))
	
	# Saving the sky image :
	
	skyimagepath = os.path.join(alidir,  image["imgname"] + "_sky.fits")
	if os.path.isfile(skyimagepath):
		os.remove(skyimagepath)
	
	shutil.move("background.fits", skyimagepath)
	
	(skya, skyh) = fromfits(os.path.join(alidir,  image["imgname"] + "_sky.fits"), verbose = False)
	(imagea, imageh) = fromfits(os.path.join(alidir, image["imgname"] + ".fits"), verbose = False)
	
	skysubimagea = imagea - skya
	
	skysubimagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
	if os.path.isfile(skysubimagepath):
		os.remove(skysubimagepath)
	
	tofits(skysubimagepath, skysubimagea, hdr = imageh, verbose = True)
	
	
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "The sky is no longer the limit. I took %s" % timetaken)


