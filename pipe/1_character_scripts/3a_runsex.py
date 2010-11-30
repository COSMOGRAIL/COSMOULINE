#
#	Runs sextractor on the input images. Next script will measure seeing + ellipticity.
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
from readandreplace_fct import *
import shutil
import os

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):

	print "- " * 30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
	imagepath = os.path.join(alidir, image['imgname']+".fits")
	
	# We run sextractor on the images converted to electrons :
	os.system("%s %s -c default_see_template.sex -GAIN %.3f -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f" % (sex, imagepath, image["gain"], image["pixsize"], image["satur_level"]))
	
	
	catfilename = os.path.join(alidir, image['imgname']+".cat")
	shutil.move("sex.cat", catfilename)
	
	
	# remove check image in case it was created
	if os.path.isfile("check.fits"):
		os.remove("check.fits")

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I'me done. It took me %s" % timetaken)

