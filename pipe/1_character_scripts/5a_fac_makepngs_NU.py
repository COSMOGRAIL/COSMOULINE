#
#    generates pngs from the fits files
#    do not forget to
#    - change the pngkey, 
#    - the region and cutoffs
#    - the resizing
#    - the sorting and naming of the images
#
import shutil
from datetime import datetime
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, nicetimediff, notify
from modules import f2n



askquestions = settings['askquestions']



# - - - CONFIGURATION - - -

crop = False
cropregion = "[330:1680,108:682]"

#rebin = 4
rebin = "auto" # either 2 or 4, depending on size of image

#z1 = -40
#z2 =  2000
z1 = "auto"
z2 = "auto"
# you could choose "auto" instead of these numerical values.

# - - - - - - - - - - - - -

print("You can configure some lines of this script.")
print("(e.g. to produce full frame pngs, or zoom on the lens, etc)")
print("I respect thisisatest, so you can use this to try your settings...")

#proquest(askquestions)

pngdir = os.path.join(settings['workdir'], "imgpngs")

if settings['update']:
    print("I will complete the existing sky folder.",
          "Or create it if you deleted it to save space")
    if not os.path.isdir(pngdir):
        os.mkdir(pngdir)

else:
    if os.path.isdir(pngdir):
        print("I will delete existing stuff.")
        proquest(askquestions)
        shutil.rmtree(pngdir)
    os.mkdir(pngdir)

# We select the images to treat :
db = KirbyBase(imgdb)
if settings['thisisatest'] :
    print("This is a test run.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], 
                              [True, True, True], 
                              returnType='dict', sortFields=['setname','mjd'])
elif settings['update']:
    print("This is an update.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], 
                              returnType='dict', sortFields=['setname','mjd'])
    askquestions=False
else :
    images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [True, True], 
                              returnType='dict', sortFields=['setname','mjd'])


print("I will treat", len(images), "images.")
proquest(askquestions)


starttime = datetime.now()


for i, image in enumerate(images):
    
    print("- " * 40)
    print(i+1, "/", len(images), ":", image['imgname'])

    
    fitsfile = os.path.join(alidir, image['imgname'] + ".fits")
    
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
    f2nimg.writetitle(image['imgname'] + ".fits")
    
    infotextlist = [
    f"{image['datet']} UTC",
    image['telescopename'] + " - " + image['setname'],
    f"Seeing : {image['seeing']:4.2f} [arcsec]",
    f"Ellipticity : {image['ell']:4.2f}",
    f"Airmass : {image['airmass']:4.2f}",
    f"Sky level : {image['skylevel']:.1f}",
    f"Sky stddev : {image['prealistddev']:.1f}"
    ]

    
    f2nimg.writeinfo(infotextlist)

    #pngname = "%04d.png" % (i+1)
    pngname = image['imgname'] + ".png"
    pngpath = os.path.join(pngdir, pngname)
    f2nimg.tonet(pngpath)

    if not settings['update']:
        # a link to get the images sorted for the movies etc.
        orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) 
        os.symlink(pngpath, orderlink)

if settings['update']:  
    # remove all the symlink and redo it again with the new images:
    allimages = db.select(imgdb, ['gogogo', 'treatme'], 
                                 [True, True], 
                                 returnType='dict', 
                                 sortFields=['setname','mjd'])
    
    for i, image in enumerate(allimages):
        pngpath = os.path.join(pngdir, image['imgname'] + ".png")
        # a link to get the images sorted for the movies etc.:
        orderlink = os.path.join(pngdir, "%05i.png" % (i+1)) 
        try:
            os.unlink(orderlink)
        except:
            pass
        os.symlink(pngpath, orderlink)



timetaken = nicetimediff(datetime.now() - starttime)
notify(computer, settings['withsound'], f"I'm done. {timetaken} .")
print("PNGs were written into")
print(pngdir)
