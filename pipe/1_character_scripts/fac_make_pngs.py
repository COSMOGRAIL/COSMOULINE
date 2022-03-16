#
#	generates pngs from the fits files of a certain set of images
#	do not forget to
#	- the region and cutoffs
#	- the resizing
#	- the sorting and naming of the images
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from star import *
import shutil
import f2n
from datetime import datetime, timedelta


# - - - CONFIGURATION - - -

# This pngkey is nothing more than the name of a directory in which the pngs will be written.
# Change it to avoid overwriting an existing set of pngs.

print("You want to make pngs for the following setname:")
print(setname)
proquest(askquestions)

pngkey = setname

crop = False
cropregion = "[330:1680,108:682]"
rebin = 1
#z1 = -40
#z2 =  2000
z1 = "auto"
z2 = "auto"
# you could choose "auto" instead of these numerical values.

# - - - - - - - - - - - - -

print("You can configure some lines of this script.")
print("(e.g. to produce full frame pngs, or zoom on the lens, etc)")
print("I respect thisisatest, so you can use this to try your settings...")

proquest(askquestions)

pngdir = os.path.join(workdir, pngkey + "_png")

# We check for potential existing stuff :
if os.path.isdir(pngdir):
	print("I will delete existing stuff.")
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

# We select the images to treat :
db = KirbyBase()
if thisisatest :
	print("This is a test run.")
	#images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['mjd'])
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist', 'setname'], [True, True, True, setname], returnType='dict', sortFields=['setname','mjd'])
else :
	#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['mjd'])
	images = db.select(imgdb, ['gogogo', 'treatme', 'setname'], [True, True, setname], returnType='dict', sortFields=['setname','mjd'])

#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['date'])
#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['seeing'])
#images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['mjd'])
#images = db.select(imgdb, ['gogogo', 'ell'], [True, ">0.65"], returnType='dict', sortFields=['mjd'])
#images = db.select(imgdb, ['recno'], ['*'], returnType='dict', sortFields=['mjd'])

print("I will treat", len(images), "images.")
proquest(askquestions)


starttime = datetime.now()


for i, image in enumerate(images):
	
	print("- " * 40)
	print(i+1, "/", len(images), ":", image['imgname'])

	
	fitsfile = image['rawimg']
	
	f2nimg = f2n.fromfits(fitsfile)
	if crop :
		f2nimg.irafcrop(cropregion)
	f2nimg.setzscale(z1, z2)
	f2nimg.rebin(rebin)
	f2nimg.makepilimage(scale = "log", negative = False)
	f2nimg.writetitle(image['imgname'])
	
	
	date = image['datet']
	seeing = "Seeing : %4.2f" % image['seeing']
	ell = "Ellipticity : %4.2f" % image['ell']
	skylevel = "Sky level : %4.2f" % image['skylevel']
	stddev = "Preali sky stddev : %4.2f" % image['prealistddev']
	airmass = "Airmass : %4.2f" % image['airmass']
	az = "Azimuth : %6.2f" % image['az']
	
	infolist = ["", date, seeing, ell, skylevel, stddev, airmass, az]
	f2nimg.writeinfo(infolist)


	# try to add new stuff: plot sextracted objects.
	print("WARNING: if you want to display these images, you need to change your default.param output parameters to: NUMBER / X_IMAGE / Y_IMAGE only you can use the imgplot.param as the PARAMETERS_NAME of your default_see_template.sex file")

	starcat = os.path.join(alidir,image["imgname"]+'.cat')
	import star
	extstars = star.readmancat(starcat)
	for star in extstars:
		f2nimg.drawcircle(star.x, star.y, r = 10, colour = 'white', label = None)


	#pngname = "%04d.png" % (i+1)
	pngname = image['imgname'] + ".png"
	pngpath = os.path.join(pngdir, pngname)
	f2nimg.tonet(pngpath)
	
	orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
	os.symlink(pngpath, orderlink)

	if i==0:
		print("Here is the first image:")
		print(pngpath)
		proquest(askquestion)


	
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
print("PNGs are written into")
print(pngdir)

if makejpgarchives :
	makejpgtgz(pngdir, workdir, askquestions = askquestions)


