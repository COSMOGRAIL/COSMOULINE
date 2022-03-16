#
#	We read your alistars.cat, and draw circles on a png of your reference image.
#	This will be handy for many tasks.
#	Plus it's nice to get a feeling about your sextractor settings ...
#	

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
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
if os.path.exists(linkpath) or os.path.islink(linkpath):
	print "Removing link..."
	os.remove(linkpath)
os.symlink(refimgpath, linkpath)

print "I made an alias to this reference image here :"
print linkpath
print "Saturation level (in e-) of ref image : %.2f" % (refimage["saturlevel"] * refimage["gain"])


print "Now I will need some alignment stars (write them into configdir/alistars.cat)."
proquest(askquestions) 

# Load the reference sextractor catalog
refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = star.readsexcat(refsexcat, maxflag = 16, posflux = True)
refautostars = star.sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']

# read and identify the manual reference catalog
refmanstars = star.readmancat(alistarscat) # So these are the "manual" star coordinates
id = star.listidentify(refmanstars, refautostars, tolerance = identtolerance, onlysingle = True, verbose = True) # We find the corresponding precise sextractor coordinates

if len (id["nomatchnames"]) != 0:
	print "Warning : the following stars could not be identified in the sextractor catalog :"
	print "\n".join(id["nomatchnames"])
	print "I will go on, disregarding these stars."
	proquest(askquestions) 
	
preciserefmanstars = star.sortstarlistbyflux(id["match"])
maxalistars = len(refmanstars)


print "%i stars in your manual star catalog." % (len(refmanstars))
print "%i stars among them could be found in the sextractor catalog." % (len(preciserefmanstars))

# The user might want to put the fluxes and precise coordinates into his mancat :
print "If you want, you could copy and paste this into your mancat (same stars, but precise coords and FLUX_AUTO) :"

for s in id["match"] : # We use this id instead of preciserefmanstars to keep them in your order
	print "%s\t%.2f\t%.2f\t%.2f" % (s.name, s.x, s.y, s.flux)

print "I can copy that in your alistars.cat, photomstars.cat and normstars.cat : "
proquest(askquestions)
f = open(configdir + "/alistars.cat", 'w')
g = open(configdir + "/photomstars.cat", 'w')
h = open(configdir + "/normstars.cat", 'w')
for s in id["match"] : # We use this id instead of preciserefmanstars to keep them in your order
	f.write("%s\t%.2f\t%.2f\t%.2f \n" % (s.name, s.x, s.y, s.flux))
	g.write("%s\t%.2f\t%.2f\t%.2f \n" % (s.name, s.x, s.y, s.flux))
	h.write("%s\t%.2f\t%.2f\t%.2f \n" % (s.name, s.x, s.y, s.flux))

f.close()

print "I will now generate a png map."
proquest(askquestions)

# We convert the star objects into dictionnaries, to plot them using f2n.py
# (f2n.py does not use these "star" objects...)
refmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refmanstars]
preciserefmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in preciserefmanstars]
refautostarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refautostars]

#print refmanstarsasdicts

if defringed:
	reffitsfile = os.path.join(alidir, refimage['imgname'] + "_defringed.fits")
else:
	if os.path.isfile(os.path.join(alidir, refimage['imgname'] + "_skysub.fits")):
		reffitsfile = os.path.join(alidir, refimage['imgname'] + "_skysub.fits")  # path to the img_skysub.fits you will display
	else:
		print "Apparently, you removed your non-ali images, I'll try to find your _ali image."
		reffitsfile = os.path.join(alidir, refimage['imgname'] + "_ali.fits")

f2nimg = f2n.fromfits(reffitsfile)
f2nimg.setzscale(z1=0, z2=1000)
#f2nimg.rebin(2)
f2nimg.makepilimage(scale = "log", negative = False)


f2nimg.drawstarlist(refautostarsasdicts, r = 30, colour = (150, 150, 150))
#f2nimg.drawstarlist(refmanstarsasdicts, r = 25, colour = (0, 0, 255))
f2nimg.drawstarlist(preciserefmanstarsasdicts, r = 5, colour = (255, 0, 0))


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



