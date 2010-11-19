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


print "Note that the program sets itself the gain and the pixel scale in the default_see.sex according to the database. Great!"
# The following line will interactively ask if you want to go on or abort.
# "askquestions" can be set to False in config.py, in which case we skip this. 
proquest(askquestions)

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')


nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

starttime = datetime.now()

# default parameter for the sextractor input

scriptdir = os.path.join(pipedir, "1_character_scripts")
key = "see"	# key is a key word according to what you're doing with sextractor (mesuring seeing: key = see)
default_template_filename = os.path.join(scriptdir, "default_" +key+ "_template.sex")
pixesize = 0.0	
gain = 0.0

sexin = "default_" +key+ ".sex" 	#name of the sextractor input file


for i,image in enumerate(images):

	print "- " * 30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
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
	
	
	sexout = os.system(sex +" "+ image['rawimg'] + " -c " +sexin)
	#print sex +" "+ filename + " -c default_see.sex"
	catfilename = alidir+image['imgname']+".cat"
	os.system("mv sex.cat "+catfilename)
	
	
	# for convenience, we make an alias to the original file
	newfilepath = alidir + image['imgname'] + ".fits"
	
	# the old way was :
	#if os.path.islink(newfilepath):
	#	os.remove(newfilepath)
	#os.symlink(image['rawimg'], newfilepath)
	
	#The new way :
	copyorlink(image['rawimg'], newfilepath, uselinks)
	
	# remove check image in case it was created
	if os.path.isfile("check.fits"):
		os.remove("check.fits")

#We delete the default_sky.sex to keep the directory clean
os.remove(os.path.join(scriptdir, sexin))

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I'me done. It took me %s" % timetaken)

