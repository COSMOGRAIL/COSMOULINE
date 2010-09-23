#
#	mimics the sky subtraction without doing anything to the images
#	we do a copy, as this is the first time we need the actual images.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta

import shutil

db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

nbrimages = len(images)

print "I will not change the images, just (link or) copy the files."
proquest(askquestions)

print "Number of images to treat :", nbrimages
proquest(askquestions)

starttime = datetime.now()


for i,image in enumerate(images):

	recno = image['recno']
	justname = image['imgname']
	filename = image['rawimg']
	print "+++++++++++++++++++++++++++++++++++++++++++++++"
	print i+1, "/", nbrimages, ":", justname
	
	#sexout = os.system(sex +" "+ filename + " -c default_sky.sex")
	#os.remove("sex.cat")
	#os.system("mv check.fits " + alidir + justname + "_skysub.fits")
	
	shutil.copy(filename, alidir + justname + "_skysub.fits")
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "Files copied. It took %s" % timetaken)


