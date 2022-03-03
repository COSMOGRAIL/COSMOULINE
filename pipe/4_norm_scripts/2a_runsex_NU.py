#
#	We run sextractor on the aligned images
#


from datetime import datetime
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import alidir, computer, imgdb, settings, sex
from modules.kirbybase import KirbyBase
from variousfct import notify, proquest, nicetimediff

askquestions = settings['askquestions']
# We select the images to treat

db = KirbyBase(imgdb)
if settings['update']:
	print("This is an update")
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], returnType='dict')
	askquestions=False
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [True, True], returnType='dict')

nbrofimages = len(images)
print("I have", nbrofimages, "images to treat.")
proquest(askquestions)

starttime = datetime.now()

for i, image in enumerate(images):

	print(" -" * 20)
	print(i+1, "/", nbrofimages, ":", image['imgname'])	
	
	imgpath = os.path.join(alidir, image['imgname'] + "_ali.fits")
	sexcatpath = os.path.join(alidir, image['imgname'] + ".alicat")
		
	# We run sextractor on the sky subtracted and aligned image :
	saturlevel = image["gain"] * image["saturlevel"] # to convert to electrons
	if image["telescopename"] in ["FORS2"]:
		print("FORS2 detected, switching to FORS extraction parameters")
		cmd = "%s %s -c default_norm_template_FORS.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CATALOG_NAME %s" % (sex, imgpath, image["pixsize"], saturlevel, sexcatpath)
	else:
		cmd = "%s %s -c default_norm_template.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CATALOG_NAME %s" % (sex, imgpath, image["pixsize"], saturlevel, sexcatpath)

	print(cmd)

	os.system(cmd)
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, settings['withsound'], "Aperture photometry done in %s" % timetaken)
	
