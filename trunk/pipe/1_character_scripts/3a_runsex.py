#
#	Runs sextractor on the input images. Next script will measure seeing + ellipticity.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError

from variousfct import *
from datetime import datetime, timedelta

print "Do not forget to update pixel size in the sextractor input."
# The following line will interactively ask if you want to go on or abort.
# "askquestions" can be set to False in config.py, in which case we skip this. 
proquest(askquestions)

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')


nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):

	print "- " * 30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
	sexout = os.system(sex +" "+ image['rawimg'] + " -c default_see.sex")
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


endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I'me done. It took me %s" % timetaken)

