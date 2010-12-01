#
#	generates pngs from the fits files of a certain set of images
#	do not forget to
#	- the region and cutoffs
#	- the resizing
#	- the sorting and naming of the images
#

execfile("./config.py")
from variousfct import *
import shutil
import f2n
from datetime import datetime, timedelta
import glob

# - - - CONFIGURATION - - -

# This pngkey is nothing more than the name of a directory in which the pngs will be written.
# Change it to avoid overwriting an existing set of pngs.

print "You want to make pngs for the set of simulated images called : ", simname
print "Is this correct, my dear master?"
proquest(askquestions)

pngkey = os.path.join(workdir, simname)

crop = False
cropregion = "[330:1680,108:682]"
rebin = 2
#z1 = -40
#z2 =  2000
z1 = "auto"
z2 = "auto"
# you could choose "auto" instead of these numerical values.

# - - - - - - - - - - - - -

print "You can configure some lines of this script."
print "(e.g. to produce full frame pngs, or zoom, etc)"
print "I respect thisisatest, so you can use this to try your settings..."

proquest(askquestions)

pngdir = os.path.join(workdir, pngkey + "_png")

# We check for potential existing stuff :
if os.path.isdir(pngdir):
	print "I will delete existing stuff."
	proquest(askquestions)
	shutil.rmtree(pngdir)
os.mkdir(pngdir)

# We select the images to treat (a list of file path)
images = glob.glob(os.path.join(workdir, simname) + "/*.fits")

print "I will treat", len(images), "images."
proquest(askquestions)


starttime = datetime.now()


for i, image in enumerate(images):
	
	print "- " * 40
	print i+1, "/", len(images), ":"

	imgname = os.path.basename(image)
	fitsfile = image
	
	f2nimg = f2n.fromfits(fitsfile)
	if crop :
		f2nimg.irafcrop(cropregion)
	f2nimg.setzscale(z1, z2)
	f2nimg.rebin(rebin)
	f2nimg.makepilimage(scale = "log", negative = False)
	f2nimg.writetitle(imgname)
	



	#pngname = "%04d.png" % (i+1)
	pngname = imgname + ".png"
	pngpath = os.path.join(pngdir, pngname)
	f2nimg.tonet(pngpath)
	
	orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) # a link to get the images sorted for the movies etc.
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

print "\nPNGs are written into"
print pngdir


print "Done."



