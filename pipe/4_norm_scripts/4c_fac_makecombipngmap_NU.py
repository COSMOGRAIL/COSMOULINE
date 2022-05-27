#
#	Similar to the 1a_checkalistars, we draw the alignment stars, this time on the combi image (to make a "nice" map)	
#	
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import alidir, settings, combibestkey, imgdb
from modules.kirbybase import KirbyBase
db = KirbyBase(imgdb)
from modules import star, f2n

refimgname = settings['refimgname']
identtolerance = settings['identtolerance']
workdir = settings['workdir']
lensregion = settings['lensregion']
emptyregion = settings['emptyregion']
xephemlens = settings['xephemlens']

# Read reference image info from database
db = KirbyBase(imgdb)

refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
refimage = refimage[0]


refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = star.readsexcat(refsexcat)
refautostars = star.sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']



# We convert the star objects into dictionnaries, to plot them using f2n.py
# (f2n.py does not use these "star" objects...)
refautostarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refautostars]

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], ['*'], ['setname'])])

for setname in usedsetnames:
    combifitsfile = os.path.join(workdir, f"{setname}_{combibestkey}.fits")
    f2nimg = f2n.fromfits(combifitsfile)
    f2nimg.setzscale(z1=-5, z2=1000)
    #f2nimg.rebin(2)
    f2nimg.makepilimage(scale = "log", negative = False)
    
    
    
    # We draw the rectangles around qso and empty region :
    
    lims = [list(map(int,x.split(':'))) for x in lensregion[1:-1].split(',')]
    
    lims = [list(map(int,x.split(':'))) for x in emptyregion[1:-1].split(',')]
    
    
    f2nimg.writetitle("%s / %s" % (xephemlens.split(",")[0], combibestkey))
    
    pngpath = os.path.join(workdir, f"{setname}_{combibestkey}.png")
    f2nimg.tonet(pngpath)
    
    print("I have written the map into :")
    print(pngpath)


