#
#	subtracts the sky from the images, using sextractor
#	We save the sky image into a file, then subtract it.
#	This has a large footprint on diskspace, but you can delete some afterwards.
#
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
from modules.variousfct import fromfits, proquest, nicetimediff, notify, tofits
from datetime import datetime

askquestions = settings['askquestions']


db = KirbyBase(imgdb)
if settings['thisisatest']:
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict')
elif settings['update']:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')
	
	
nbrimages = len(images)
print("Number of images to treat :", nbrimages)
proquest(askquestions)

starttime = datetime.now()

redofromscratch = True

for i,image in enumerate(images):
	
	print("+ " * 30)
	print("%5i/%i : %s" % (i+1, nbrimages, image["imgname"]))
	
	imagepath = os.path.join(alidir, image["imgname"] + ".fits")
	skyimagepath = os.path.join(alidir,  image["imgname"] + "_sky.fits")
	if os.path.isfile(skyimagepath):
		if redofromscratch:
			print("Removing existing sky image.")
			os.remove(skyimagepath)
		else:
			print("Already done, I skip this one...")
			continue
	
	# We run sextractor  on the image in electrons :
	saturlevel = image["gain"] * image["saturlevel"] # to convert to electrons
	
	if image["telescopename"] in ["EulerCAM", "SMARTSandicam", "GMOS"]:
		print("Detected fine pixel telescope, switching to smooth sky")
		cmd = "%s %s -c default_sky_template_smooth.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CHECKIMAGE_NAME %s" % (sex, imagepath, image["pixsize"], saturlevel, skyimagepath)


	elif image["telescopename"] in ["FORS2"]:
		print("FORS2 detected, switching to FORS sky")
		cmd = "%s %s -c default_sky_template_FORS.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CHECKIMAGE_NAME %s" % (sex, imagepath, image["pixsize"], saturlevel, skyimagepath)
	else:
		cmd = "%s %s -c default_sky_template_smooth.sex -PIXEL_SCALE %.3f -SATUR_LEVEL %.3f -CHECKIMAGE_NAME %s" % (sex, imagepath, image["pixsize"], saturlevel, skyimagepath)

	#print cmd
	os.system(cmd)
	
	(skya, skyh) = fromfits(skyimagepath, verbose = False)
	(imagea, imageh) = fromfits(imagepath, verbose = False)
	
	skysubimagea = imagea - skya
	
	skysubimagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
	if os.path.isfile(skysubimagepath):
		print("Removing existing skysubtracted image.")
		os.remove(skysubimagepath)
	
	tofits(skysubimagepath, skysubimagea, hdr = imageh, verbose = True)
	
	
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, settings['withsound'], "The sky is no longer the limit. I took %s" % timetaken)


