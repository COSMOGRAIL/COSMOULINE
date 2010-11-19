#
#	We read your alistars.cat, and draw circles on a png of your reference image.
#	This will be handy for many tasks.
#	Plus it's nice to get a feeling about your sextractor settings ...
#	

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from star import *
#import shutil
import f2n
#from datetime import datetime, timedelta


# Read reference image info from database
db = KirbyBase()

print "From here on I need a reference image (write it into configdir/settings.py)."
print "You have chosen %s as reference." % refimgname
refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
if len(refimage) != 1:
	print "Reference image identification problem !"
	sys.exit()
refimage = refimage[0]

# We put an alias to the reference image into the workdir (for humans only) :

refimgpath = os.path.join(alidir, refimage["imgname"] + ".fits")
linkpath = os.path.join(workdir, "ref.fits")
if os.path.isfile(linkpath):
	os.remove(linkpath)
os.symlink(refimgpath, linkpath)

print "I made an alias to this reference image here :"
print linkpath


print "Now I will need some alignment stars (write them into configdir/alistars.cat)."
proquest(askquestions) 

# Load the reference sextractor catalog
refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = readsexcatasstars(refsexcat)
refautostars = sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']

# read and identify the manual reference catalog
refmanstars = readmancatasstars(alistarscat) # So these are the "manual" star coordinates
preciserefmanstars = listidentify(refmanstars, refautostars, 3.0) # We find the corresponding precise sextractor coordinates
preciserefmanstars = sortstarlistbyflux(preciserefmanstars)
maxalistars = len(refmanstars)


print "%i stars in your manual star catalog." % (len(refmanstars))
print "%i stars among them could be found in the sextractor catalog." % (len(preciserefmanstars))

# We convert the star objects into dictionnaries, to plot them using f2n.py
# (f2n.py does not use these "star" objects...)
refmanstarsasdicts = [{"name":star.name, "x":star.x, "y":star.y} for star in refmanstars]
preciserefmanstarsasdicts = [{"name":star.name, "x":star.x, "y":star.y} for star in preciserefmanstars]
refautostarsasdicts = [{"name":star.name, "x":star.x, "y":star.y} for star in refautostars]

#print refmanstarsasdicts

reffitsfile = os.path.join(alidir, refimage['imgname'] + "_skysub.fits")

f2nimg = f2n.fromfits(reffitsfile)
f2nimg.setzscale(z1=0, z2=1000)
#f2nimg.rebin(2)
f2nimg.makepilimage(scale = "log", negative = False)


f2nimg.drawstarslist(refautostarsasdicts, r = 30, colour = (150, 150, 150))
#f2nimg.drawstarslist(refmanstarsasdicts, r = 25, colour = (0, 0, 255))
f2nimg.drawstarslist(preciserefmanstarsasdicts, r = 5, colour = (255, 0, 0))


f2nimg.writeinfo(["Sextractor stars (flag-filtered) : %i" % len(refautostarsasdicts)], colour = (150, 150, 150))
#f2nimg.writeinfo(["", "Stars that you dutifully wrote in the alignment star catalog : %i" % len(refmanstarsasdicts)], colour = (0, 0, 255))
f2nimg.writeinfo(["","Identified alignment stars with corrected sextractor coordinates : %i" % len(preciserefmanstarsasdicts)], colour = (255, 0, 0))


# We draw the rectangles around qso and empty region :

lims = [map(int,x.split(':')) for x in lensregion[1:-1].split(',')]
f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Lens")

lims = [map(int,x.split(':')) for x in emptyregion[1:-1].split(',')]
f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Empty")


f2nimg.writetitle("Ref : " + refimage['imgname'])

pngpath = os.path.join(workdir, "alistars.png")
f2nimg.tonet(pngpath)

print "I have written a map into"
print pngpath


# Now we also put an alias to the reference image into the workdir (for humans only) :

fullrefimgname = refimgname + ".fits"
#linkname = "ref.fits"
#if os.path.isfile(linkname):
#	os.remove(linkname)
#os.symlink(fullrefimgname, linkname)
#os.chdir(curdir)


