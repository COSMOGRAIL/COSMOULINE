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

redofromscratch = False
manual = False

db = KirbyBase()
if thisisatest:
    print "This is a test run."
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict',
                       sortFields=['setname', 'mjd'])
elif update:
    print "This is an update."
    images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict',
                       sortFields=['setname', 'mjd'])
    askquestions = False
else:
    print "I will create sky png only for a sample of images."
    images = []
    if manual:
        set_number = int(input("How many set of images do you have ? "))
        im_number = int(input("How many images per set do you want to take ? "))
    else:
        set_number = 3
        im_number = 10
    for i in range(set_number):
        im = db.select(imgdb, ['gogogo', 'treatme', 'setname'], [True, True, str(i + 1)], returnType='dict', sortFields=['mjd'])
        im = im[:im_number]
        images = images + im

nbrimages = len(images)
print "Number of images to treat :", nbrimages
proquest(askquestions)

pngdirpath = os.path.join(workdir,
                          "sky_png")  # this is where you will put the png images (maybe move the whole name architecture into a single parameterfile ?)

if update:
    print "I will complete the existing sky folder. Or create it if you deleted it to save space"
    if not os.path.isdir(pngdirpath):
        os.mkdir(pngdirpath)

else:
    if os.path.isdir(pngdirpath):
        if redofromscratch:
            print "I will delete existing stuff."
            proquest(askquestions)
            shutil.rmtree(pngdirpath)
            os.mkdir(pngdirpath)
        else:
            print "I will complete the existing folder"
            proquest(askquestions)
    else:
        os.mkdir(pngdirpath)

starttime = datetime.now()

errmsg = ''
for i, image in enumerate(images):
    try:
        print "+ " * 30
        print "%5i/%i : %s" % (i + 1, nbrimages, image["imgname"])

        pngpath = os.path.join(pngdirpath, "%s_sky.png" % image['imgname'])
        if os.path.isfile(pngpath) and not redofromscratch:
            print "File exists, I skip..."
            continue

        skyimagepath = os.path.join(alidir, image["imgname"] + "_sky.fits")
        skysubimagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")

        skyimage = f2n.fromfits(skyimagepath)
        skyimage.setzscale("ex", "ex")
        skyimage.rebin(3)
        skyimage.makepilimage(scale="lin", negative=False)
        skyimage.upsample(2)
        skyimage.writetitle("Sky", colour=(255, 0, 0))

        skysubimage = f2n.fromfits(skysubimagepath)
        skysubimage.setzscale("auto", "auto")
        skysubimage.rebin(3)
        skysubimage.makepilimage(scale="log", negative=False)
        skysubimage.upsample(2)
        skysubimage.writetitle("Skysubtracted image")

        # We read the 20 strongest stars from sextractor :
        sexcatpath = os.path.join(alidir, image['imgname'] + ".cat")
        sexcat = star.readsexcat(sexcatpath)
        sexcat = star.sortstarlistbyflux(sexcat)
        sexcatasdicts = [{"name": s.name, "x": s.x, "y": s.y} for s in sexcat[:20]]

        skysubimage.drawstarlist(sexcatasdicts, r=30, colour=(255, 255, 255))
        skyimage.drawstarlist(sexcatasdicts, r=30, colour=(255, 0, 0))

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
        skysubimage.writeinfo(skysubinfo, colour=(255, 255, 255))

        skyinfo = [
            "%s : %i -> %i (span = %i) [ADU]" % ("Cuts", skyimage.z1, skyimage.z2, skyimage.z2 - skyimage.z1)
        ]
        skyimage.writeinfo(skyinfo, colour=(255, 0, 0))

        f2n.compose([[skysubimage, skyimage]], pngpath)

        if not update:
            orderlink = os.path.join(pngdirpath,
                                     "%05i.png" % (i + 1))  # a link to get the images sorted for the movies etc.
            os.symlink(pngpath, orderlink)
    except:
        errmsg += "%s \n" % image["imgname"]

if errmsg != '':
    print "\n Problem with the following images:\n" + errmsg
    print "Check the fits !!"

if update:  # remove all the symlink and redo it again with the new images
    allimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])
    for i, image in enumerate(allimages):
        pngpath = os.path.join(pngdirpath, "%s_sky.png" % image['imgname'])
        orderlink = os.path.join(pngdirpath,
                                 "%05i.png" % (i + 1))  # a link to get the images sorted for the movies etc.
        try:
            os.unlink(orderlink)
        except:
            pass
        os.symlink(pngpath, orderlink)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)
notify(computer, withsound, "PNGs written in %s I took %s" % (pngdirpath, timetaken))

if makejpgarchives:
    makejpgtgz(pngdirpath, workdir, askquestions=askquestions)



