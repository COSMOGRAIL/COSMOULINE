#
#	Similar to the 1a_checkalistars, we draw the alignment stars, this time on the combi image (to make a "nice" map)	
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

refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
refimage = refimage[0]


refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = star.readsexcat(refsexcat)
refautostars = star.sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']

# read and identify the manual reference catalog
refmanstars = star.readmancat(alistarscat) # So these are the "manual" star coordinates
id = star.listidentify(refmanstars, refautostars, tolerance = identtolerance) # We find the corresponding precise sextractor coordinates
preciserefmanstars = star.sortstarlistbyflux(id["match"])
maxalistars = len(refmanstars)


print "%i stars in your manual star catalog." % (len(refmanstars))
print "%i stars among them could be found in the sextractor catalog." % (len(preciserefmanstars))

# We convert the star objects into dictionnaries, to plot them using f2n.py
# (f2n.py does not use these "star" objects...)
refmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refmanstars]
preciserefmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in preciserefmanstars]
refautostarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refautostars]

#print refmanstarsasdicts

combifitsfile = os.path.join(workdir, "%s.fits" % combibestkey)
#combifitsfile = os.path.join(workdir, "ali", "%s_ali.fits" % refimgname)
f2nimg = f2n.fromfits(combifitsfile)
f2nimg.setzscale(z1=-5, z2=1000)
#f2nimg.rebin(2)
f2nimg.makepilimage(scale = "log", negative = False)


#f2nimg.drawstarlist(refautostarsasdicts, r = 30, colour = (150, 150, 150))
#f2nimg.drawstarlist(preciserefmanstarsasdicts, r = 7, colour = (255, 0, 0))


#f2nimg.writeinfo(["Sextractor stars (flag-filtered) : %i" % len(refautostarsasdicts)], colour = (150, 150, 150))
#f2nimg.writeinfo(["","Identified alignment stars with corrected sextractor coordinates : %i" % len(preciserefmanstarsasdicts)], colour = (255, 0, 0))


# We draw the rectangles around qso and empty region :

lims = [map(int,x.split(':')) for x in lensregion[1:-1].split(',')]
#f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Lens")

lims = [map(int,x.split(':')) for x in emptyregion[1:-1].split(',')]
#f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Empty")


f2nimg.writetitle("%s / %s" % (xephemlens.split(",")[0], combibestkey))

pngpath = os.path.join(workdir, "%s.png" % combibestkey)
f2nimg.tonet(pngpath)

print "I have written the map into :"
print pngpath

# print "Do you want to clean the selected image to save some space on the disk ? "
# proquest(True)
#
# combidir = os.path.join(workdir, combibestkey)
# os.remove(combidir)

