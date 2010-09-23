#
#	We run sextractor on the aligned images
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta


print "Hola amigo : don't forget to check the sextractor configuration !"
print "Put the pixel size of the reference frame."
proquest(askquestions)

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], ['recno','imgname'], returnType='dict')

nbrofimages = len(images)
print "I have", nbrofimages, "images to treat."
proquest(askquestions)


starttime = datetime.now()

for i, image in enumerate(images):

	print " -" * 20
	print i+1, "/", nbrofimages, ":", image['imgname']	
	img = alidir + image['imgname'] + "_ali.fits"
	sexcat = alidir + image['imgname'] + ".alicat"
	
	sexout = os.system(sex +" "+ img + " -c default_norm.sex")
	os.system("mv sex.cat " + sexcat)
	#os.system("rm check.fits")

	
#db.pack(imgdb) # to erase the blank lines

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "Aperture photometry done in %s" % timetaken)



print "Done."
	
	
