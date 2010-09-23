#
#	subtracts the sky from the images, using sextractor
#	You can switch a line below (and change the default.sex !) to save it as a "background" image.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta

print "Same here : please change pixel size in sextractor input by hand."
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

for i,image in enumerate(images):

	recno = image['recno']
	justname = image['imgname']
	filename = image['rawimg']
	print "+++++++++++++++++++++++++++++++++++++++++++++++"
	print i+1, "/", nbrimages, ":", justname
	
	sexout = os.system(sex +" "+ filename + " -c default_sky.sex")
	os.remove("sex.cat")
	
	# The normal way to go, saving the skysubtracted image :
	os.system("mv check.fits " + alidir + justname + "_skysub.fits")
	
	# But maybe you want to have a look at the subtracted background (change sextractor !)
	#os.system("mv check.fits " + alidir + justname + "_background.fits")
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "The sky is no longer the limit. I took %s" % timetaken)


