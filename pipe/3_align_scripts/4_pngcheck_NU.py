#
#	generates pngs from the aligned fits files
#	do not forget to
#	- change the pngkey, 
#	- the region and cutoffs
#	- the resizing
#	- the sorting and naming of the images
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import shutil
import f2n
from datetime import datetime, timedelta
import os, sys

# - - - CONFIGURATION - - -

# This pngkey is nothing more than the name of a directory in which the pngs will be written.
# Change it to avoid overwriting an existing set of pngs.

pngkey = "full"

crop = False
cropregion = "[330:1680,108:682]"

#rebin = 4
rebin = "auto" # either 2 or 4, depending on size of image

z1 = -40
z2 =  2000
#z1 = "auto"
#z2 = "auto"
# you could choose "auto" instead of these numerical values.

# - - - - - - - - - - - - -

print "You can configure some lines of this script."
print "(e.g. to produce full frame pngs, or zoom on the lens, etc)"
print "I respect thisisatest, so you can use this to try your settings..."

#proquest(askquestions)

pngdir = os.path.join(workdir, "ali_" + pngkey + "_png")

if update:
	print "I will complete the existing sky folder. Or create it if you deleted it to save space"
	if not os.path.isdir(pngdir):
		os.mkdir(pngdir)

else:
	if os.path.isdir(pngdir):
		print "I will delete existing stuff."
		proquest(askquestions)
		shutil.rmtree(pngdir)
	os.mkdir(pngdir)

# We select the images to treat :
db = KirbyBase()
if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname','mjd'])
elif update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict', sortFields=['setname','mjd'])
	askquestions=False
else :
	#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['mjd'])
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname','mjd'])

#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['date'])
#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['seeing'])
#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['mjd'])
#images = db.select(imgdb, ['gogogo', 'ell'], [True, ">0.65"], returnType='dict', sortFields=['mjd'])
#images = db.select(imgdb, ['recno'], ['*'], returnType='dict', sortFields=['mjd'])

print "I will treat", len(images), "images."
proquest(askquestions)

# We get the ref image to draw the ali stars, as for 1a_checkalistars.py etc :
refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
refimage = refimage[0]
refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = star.readsexcat(refsexcat)
refautostars = star.sortstarlistbyflux(refautostars)
refmanstars = star.readmancat(alistarscat) # So these are the "manual" star coordinates
id = star.listidentify(refmanstars, refautostars, tolerance = identtolerance) # We find the corresponding precise sextractor coordinates
preciserefmanstars = star.sortstarlistbyflux(id["match"])
preciserefmanstarsasdicts = [{"name":star.name, "x":star.x, "y":star.y} for star in preciserefmanstars]

starttime = datetime.now()


for i, image in enumerate(images):
	
	print "- " * 40
	print i+1, "/", len(images), ":", image['imgname']

	
	fitsfile = os.path.join(alidir, image['imgname'] + "_ali.fits")
	
	f2nimg = f2n.fromfits(fitsfile)
	if crop :
		f2nimg.irafcrop(cropregion)
	f2nimg.setzscale(z1, z2)
	
	if rebin == "auto":
		if f2nimg.numpyarray.shape[0] > 3000:
			f2nimg.rebin(4)
		else:
			f2nimg.rebin(2)
	else:
		f2nimg.rebin(rebin)
		
	f2nimg.makepilimage(scale = "log", negative = False)
	f2nimg.writetitle(image['imgname'] + "_ali.fits")
	
	infotextlist = [
	"%s UTC" % image['datet'],
	image['telescopename'] + " - " + image['setname'],
	"Seeing : %4.2f [arcsec]" % image['seeing'],
	"Ellipticity : %4.2f" % image['ell'],
	"Airmass : %4.2f" % image['airmass'],
	"Sky level : %.1f" % image['skylevel'],
	"Sky stddev : %.1f" % image['prealistddev'],
	"Nbr alistars : " + "%2i / %2i = "%(image['nbralistars'], image['maxalistars']) + "|"*image['nbralistars'],
	"Actual geomap rms : %4.2f [pixel]" % image['geomaprms'],
	"Rotator (header) : %7.2f [deg]" % image['rotator'],
	"Guessed angle : %9.4f [deg]" % image['angle'],
	"Actual geomap angle : %9.4f [deg]" % image['geomapangle'],
	"Alignment info : %s" % image['alicomment']
	]
	
	f2nimg.drawstarlist(preciserefmanstarsasdicts, r = 20, colour = None)

	
	f2nimg.writeinfo(infotextlist)

	#pngname = "%04d.png" % (i+1)
	pngname = image['imgname'] + ".png"
	pngpath = os.path.join(pngdir, pngname)
	f2nimg.tonet(pngpath)

	if not update:
		orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
		os.symlink(pngpath, orderlink)

if update:  # remove all the symlink and redo it again with the new images
	allimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname','mjd'])
	for i, image in enumerate(allimages):
		pngpath = os.path.join(pngdir, image['imgname'] + ".png")
		orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
		try:
			os.unlink(orderlink)
		except:
			pass
		os.symlink(pngpath, orderlink)

	
#origdir = os.getcwd()
#os.chdir(alidir)
#cmd = "tar cvf " + pngkey + ".tar " + pngkey + "/"
#os.system(cmd)
#cmd = "mv " + pngkey + ".tar ../."
#os.system(cmd)
#os.chdir(origdir)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)
notify(computer, withsound, "I'm done. %s ." % timetaken)
print "PNGs are written into"
print pngdir

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)


