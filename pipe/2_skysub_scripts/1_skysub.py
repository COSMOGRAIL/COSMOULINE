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

print "Note that the program sets itself the gain, the satur level and the pixel scale in the default.sex according to the database. Great!"
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
satur_level = 0.0
satur_levelADU = 65000.0

sexin = "default_" +key+ ".sex" 	#name of the sextractor input file


for i,image in enumerate(images):

	recno = image['recno']
	justname = image['imgname']
	filename = os.path.join(alidir,justname + ".fits")	# we use now the images in electron not the raw images anymore
	
	print "+++++++++++++++++++++++++++++++++++++++++++++++"
	print i+1, "/", nbrimages, ":", justname
	
	# I write default_sky.sex
		
	pixesize = image["pixsize"]
	gain = image["gain"]

	if image[combinumname] < 0.0:		#in this case, we have a combine image and therefore the satur_level must be multiply by the number of combined images
		satur_level = image["origin_gain"]*satur_levelADU*image["preredfloat1"]
		print "Combinumname : ", image[combinumname]
	else:
		satur_level = image["origin_gain"]*satur_levelADU

	default_sky_template = justread(default_template_filename)
	defaultdict = {"$gain$": str(image["gain"]), "$px_size$": str(image["pixsize"]), "$satur_level$": str(satur_level)}
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


