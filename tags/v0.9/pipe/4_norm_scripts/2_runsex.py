#
#	We run sextractor on the aligned images
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

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], ['recno','imgname','pixsize', 'gain'], returnType='dict')

nbrofimages = len(images)
print "I have", nbrofimages, "images to treat."
proquest(askquestions)


starttime = datetime.now()

# default parameter for the sextractor input

scriptdir = os.path.join(pipedir, "4_norm_scripts")
key = "norm"	# key is a key word according to what you're doing with sextractor (mesuring seeing: key = see)
default_template_filename = os.path.join(scriptdir, "default_" +key+ "_template.sex")
pixesize = 0.0	
gain = 0.0

sexin = "default_" +key+ ".sex" 	#name of the sextractor input file

for i, image in enumerate(images):

	print " -" * 20
	print i+1, "/", nbrofimages, ":", image['imgname']	
	img = alidir + image['imgname'] + "_ali.fits"
	sexcat = alidir + image['imgname'] + ".alicat"
	
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
	
	
	sexout = os.system(sex +" "+ img + " -c " +sexin)
	
	os.system("mv sex.cat " + sexcat)
	#os.system("rm check.fits")


#We delete the default_sky.sex to keep the directory clean
os.remove(os.path.join(scriptdir, sexin))

#db.pack(imgdb) # to erase the blank lines

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "Aperture photometry done in %s" % timetaken)



print "Done."
	
	