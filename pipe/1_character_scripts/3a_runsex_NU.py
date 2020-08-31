#
#	Runs sextractor on the input images. Next script will measure seeing + ellipticity.
#


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
#from readandreplace_fct import *
import shutil
import os



db = KirbyBase()
if thisisatest:
	print "This is a test run."
	images = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict')
elif update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')


nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):

	print "- " * 30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
	imagepath = os.path.join(alidir, image['imgname']+".fits")
	catfilename = os.path.join(alidir, image['imgname']+".cat")

	saturlevel = image["gain"] * image["saturlevel"] # to convert to electrons
	if image["telescopename"] in ["FORS2"]:
		print "FORS2 detected, switch to fors2 extraction parameters:"
		cmd = "%s %s -c default_see_template_FORS.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CATALOG_NAME %s" % (sex, imagepath, image["pixsize"], saturlevel, catfilename)

	else:
		cmd = "%s %s -c default_see_template.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CATALOG_NAME %s" % (sex, imagepath, image["pixsize"], saturlevel, catfilename)
	os.system(cmd)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I'me done. It took me %s" % timetaken)
