#
#	Similar to the 1a_checkalistars, we draw the alignment stars, this time on the combi image (to make a "nice" map)	
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

refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
refimage = refimage[0]


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

combifitsfile = os.path.join(workdir, "%s.fits" % combibestkey)

f2nimg = f2n.fromfits(combifitsfile)
f2nimg.setzscale(z1=-5, z2=1000)
#f2nimg.rebin(2)
f2nimg.makepilimage(scale = "log", negative = False)


#f2nimg.drawstarslist(refautostarsasdicts, r = 30, colour = (150, 150, 150))
f2nimg.drawstarslist(preciserefmanstarsasdicts, r = 7, colour = (255, 0, 0))


#f2nimg.writeinfo(["Sextractor stars (flag-filtered) : %i" % len(refautostarsasdicts)], colour = (150, 150, 150))
#f2nimg.writeinfo(["","Identified alignment stars with corrected sextractor coordinates : %i" % len(preciserefmanstarsasdicts)], colour = (255, 0, 0))


# We draw the rectangles around qso and empty region :

lims = [map(int,x.split(':')) for x in lensregion[1:-1].split(',')]
f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Lens")

lims = [map(int,x.split(':')) for x in emptyregion[1:-1].split(',')]
f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Empty")


f2nimg.writetitle("%s / %s" % (xephemlens.split(",")[0], combibestkey))

pngpath = os.path.join(workdir, "%s.png" % combibestkey)
f2nimg.tonet(pngpath)

print "I have written the map into :"
print pngpath

