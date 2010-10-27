#
#	subtracts the sky from the images, using sextractor
#	You can switch a line below (and change the default.sex !) to save it as a "background" image.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
from readandreplace_fct import *
import shutil
import os

print "Note that the program sets itself the gain and the pixel scale in the default.sex according to the database. Great!"
proquest(askquestions)

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

# default parameter for the sextractor input

scriptdir = os.path.join(pipedir, "2_skysub_scripts")
key = "sky"	# key is a key word according to what you're doing with sextractor (mesuring seeing: key = see)
default_template_filename = os.path.join(scriptdir, "default_" +key+ "_template.sex")
pixesize = 0.0	
gain = 0.0

sexin = "default_" +key+ ".sex" 	#name of the sextractor input file


for i,image in enumerate(images):

	recno = image['recno']
	justname = image['imgname']
	filename = image['rawimg']
	
	print "+++++++++++++++++++++++++++++++++++++++++++++++"
	print i+1, "/", nbrimages, ":", justname
	
	if pixesize != image["pixsize"] or gain != image["gain"]:
		# I write default_sky.sex
		
		pixesize = image["pixsize"]
		gain = image["gain"]
	
		default_sky_template = justread(default_template_filename)
		defaultdict = {"$gain$": str(image["gain"]), "$px_size$": str(image["pixsize"])}
		defaultsex = justreplace(default_sky_template, defaultdict)
		defaultfile = open(os.path.join(scriptdir, sexin), "w")	
		defaultfile.write(defaultsex)
		defaultfile.close()
		
		print "Wrote default_sky.sex"
		
	
	sexout = os.system(sex +" "+ filename + " -c " +sexin)
	os.remove("sex.cat")
	
	# The normal way to go, saving the skysubtracted image :
	os.system("mv check.fits " + alidir + justname + "_skysub.fits")
	
	# But maybe you want to have a look at the subtracted background (change sextractor !)
	#os.system("mv check.fits " + alidir + justname + "_background.fits")
	
	
	
#We delete the default_sky.sex to keep the directory clean
os.remove(os.path.join(scriptdir, sexin))

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "The sky is no longer the limit. I took %s" % timetaken)


