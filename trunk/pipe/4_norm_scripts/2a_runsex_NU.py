#
#	We run sextractor on the aligned images
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
#from readandreplace_fct import *
import shutil
import os


# We select the images to treat

db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "I have", nbrofimages, "images to treat."
proquest(askquestions)

starttime = datetime.now()

for i, image in enumerate(images):

	print " -" * 20
	print i+1, "/", nbrofimages, ":", image['imgname']	
	
	imgpath = os.path.join(alidir, image['imgname'] + "_ali.fits")
	sexcatpath = os.path.join(alidir, image['imgname'] + ".alicat")
		
	# We run sextractor on the sky subtracted and aligned image :
	saturlevel = image["gain"] * image["saturlevel"] # to convert to electrons
	if image["telescopename"] in ["FORS2"]:
		print "FORS2 detected, switching to FORS extraction parameters"
		cmd = "%s %s -c default_norm_template_FORS.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CATALOG_NAME %s" % (sex, imgpath, image["pixsize"], saturlevel, sexcatpath)
	else:
		cmd = "%s %s -c default_norm_template.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CATALOG_NAME %s" % (sex, imgpath, image["pixsize"], saturlevel, sexcatpath)

	print cmd

	os.system(cmd)
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "Aperture photometry done in %s" % timetaken)
	
