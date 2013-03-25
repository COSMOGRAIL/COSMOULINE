#
#	Control png of the image and sky
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import shutil
import os
import f2n
import star


db = KirbyBase()
if thisisatest:
	print "This is a test run."
	images = db.select(imgdb, ['gogogo','treatme','testlist'], [True, True, True], returnType='dict', sortFields=['setname','mjd'])
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict', sortFields=['setname','mjd'])
	
	
nbrimages = len(images)
print "Number of images to treat :", nbrimages
proquest(askquestions)


pngdirpath = os.path.join(workdir, "sky_png")
if os.path.isdir(pngdirpath):
	print "I will delete existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdirpath)
os.mkdir(pngdirpath)


starttime = datetime.now()

for i,image in enumerate(images):
	
	print "+ " * 30
	print "%5i/%i : %s" % (i+1, nbrimages, image["imgname"])
	
	
	skyimagepath = os.path.join(alidir,  image["imgname"] + "_sky.fits")
	skysubimagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
	
	
	
	skyimage = f2n.fromfits(skyimagepath)
	skyimage.setzscale("ex", "ex")
	skyimage.rebin(3)
	skyimage.makepilimage(scale = "lin", negative = False)
	skyimage.writetitle("Sky", colour=(255, 0, 0))
	
	skysubimage = f2n.fromfits(skysubimagepath)
	skysubimage.setzscale("auto", "auto")
	skysubimage.rebin(3)
	skysubimage.makepilimage(scale = "log", negative = False)
	skysubimage.writetitle("Skysubtracted image")
	
	# We read the 20 strongest stars from sextractor :
	sexcatpath = os.path.join(alidir, image['imgname'] + ".cat")
	sexcat = star.readsexcat(sexcatpath)
	sexcat = star.sortstarlistbyflux(sexcat)
	sexcatasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in sexcat[:20]]
	
	skysubimage.drawstarlist(sexcatasdicts, r = 30, colour = (255, 255, 255))
	skyimage.drawstarlist(sexcatasdicts, r = 30, colour = (255, 0, 0))

	skysubinfo = [
	"%s" % image["imgname"],
	"%s UTC" % image['datet'],
	image['telescopename'] + " - " + image['setname'],
	"Seeing : %4.2f [arcsec]" % image['seeing'],
	"Ellipticity : %4.2f" % image['ell'],
	"Airmass : %4.2f" % image['airmass'],
	"Sky level : %.1f" % image['skylevel'],
	"Sky stddev : %.1f" % image['prealistddev'],
	]
	skysubimage.writeinfo(skysubinfo, colour = (255, 255, 255))
	
	skyinfo = [
	"%s : %i -> %i (span = %i) [ADU]" % ("Cuts", skyimage.z1, skyimage.z2, skyimage.z2 - skyimage.z1)
	]
	skyimage.writeinfo(skyinfo, colour = (255, 0, 0))
	
	

	
	pngpath = os.path.join(pngdirpath, "%s_sky.png" % image['imgname'])
	f2n.compose([[skysubimage, skyimage]], pngpath)

	orderlink = os.path.join(pngdirpath, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
	os.symlink(pngpath, orderlink)
	


endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)
notify(computer, withsound, "PNGs written in %s I took %s" % (pngdirpath, timetaken))

if makejpgarchives :
	makejpgtgz(pngdirpath, workdir, askquestions = askquestions)



