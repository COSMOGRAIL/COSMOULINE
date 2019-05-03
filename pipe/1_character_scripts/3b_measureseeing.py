#
#	Calculates the seeing etc of the images and updates the database.
#	You can turn on the flag "checkplots" to check how I do this.
#	In this case I will not update the database.
#

forceseeingpixels = True

execfile("../config.py")
from kirbybase import KirbyBase, KBError

from variousfct import *
import star
import numpy as np

if checkplots:
    import matplotlib.pyplot as plt

db = KirbyBase()
if thisisatest:
    print "This is a test !"
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict')
elif update:
    print "This is an update !"
    images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict')
    askquestions = False
else:
    images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

if not checkplots:
    # We make a backup copy of our database.
    backupfile(imgdb, dbbudir, "seeing")

    # We add some new fields into the holy database.
    if "seeing" not in db.getFieldNames(imgdb):
        db.addFields(imgdb, ['seeing:float', 'ell:float', 'goodstars:int', 'seeingpixels:float', 'pa:float'])

    if "pa" not in db.getFieldNames(imgdb):
        db.addFields(imgdb, ['pa:float'])

    if "pastd" not in db.getFieldNames(imgdb):
        db.addFields(imgdb, ['pastd:float'])

    if "bimage" not in db.getFieldNames(imgdb):
        db.addFields(imgdb, ['bimage:float'])

    if "aimage" not in db.getFieldNames(imgdb):
        db.addFields(imgdb, ['aimage:float'])

for i, image in enumerate(images):

    print "- " * 40
    print i + 1, "/", nbrofimages, ":", image['imgname']

    catfilename = alidir + image['imgname'] + ".cat"

    # We read and sort the sextractor catalog
    goodsexstars = star.readsexcat(catfilename, maxflag=2, posflux=True,
                                   propfields=["THETA_IMAGE", "B_IMAGE", "A_IMAGE"])
    nbrstars = len(goodsexstars)
    sortedsexstars = star.sortstarlistby(goodsexstars, 'fwhm')
    # print "Best and worst FWHM:"
    # sortedsexstars[0].write()
    # sortedsexstars[-1].write()

    # Just to make the optional plot work in any case :
    peakpos = -5.0

    # We make an array to measure the seeing
    fwhms = np.array([s.fwhm for s in sortedsexstars])

    if len(fwhms) > 10:

        # We want a crude guess at what kind of range we have to look for stars
        # The goal here is to have a "nice-looking" histogram with a well defined
        # peak somewhere inside the range.

        minfwhm = 1.5
        medfwhm = np.median(fwhms)
        if medfwhm < minfwhm:
            medfwhm = minfwhm

        # stdfwhm = np.std(fwhms)
        # widestars = medfwhm + 2.0 * stdfwhm

        widestars = 3.0 * medfwhm

        maxfwhm = 30.0
        if widestars < maxfwhm:
            maxfwhm = widestars

        # At this point the true seeing should be between minfwhm and maxfwhm.

        # We build a first histogram :

        (hist, edges) = np.histogram(fwhms, bins=10,
                                     range=(minfwhm, maxfwhm))  # I removed new=True, depreciated since python 1.4
        # Note that points outside the range are not taken into account at all, they don't fill the side bins !

        # We find the peak, and build a narrower hist around it
        maxpos = np.argmax(hist)
        if maxpos == 0:
            # print "FWHMs ="
            # print "\n".join(["%.3f" % (fwhm) for fwhm in fwhms])
            # raise mterror("This FWHM distribution is anormal (many cosmics). Something is wrong with sextractor... Problematic img: " + image['imgname'])
            print "This image has many low-FWHM objects (cosmics ?)"
            seeingpixels = np.median(fwhms)
            if forceseeingpixels:
                if seeingpixels < 2:
                    seeingpixels = 2.01  # HAAAAAAX
            seeing = seeingpixels * image['pixsize']

        elif maxpos == len(hist) - 1:
            print "This image if funny, it seems to have many high-FWHM objects."
            print "I can only make a crude guess ..."
            seeingpixels = np.median(fwhms)
            if forceseeingpixels:
                if seeingpixels < 2:
                    seeingpixels = 2.01  # HAAAAAAX
            seeing = seeingpixels * image['pixsize']


        else:  # the normal situation :
            peakpos = 0.5 * (edges[maxpos] + edges[maxpos + 1])

            # We build a second histogram around this position, with a narrower range :
            (hist, edges) = np.histogram(fwhms, bins=10, range=(
            peakpos - 2.0, peakpos + 2.0))  # I removed new=True, depreciated since python 1.4
            maxpos = np.argmax(hist)
            peakpos = 0.5 * (edges[maxpos] + edges[maxpos + 1])

            # We take the median of values around this peakpos :
            starfwhms = fwhms[np.logical_and(fwhms > peakpos - 1.0, fwhms < peakpos + 1.0)]
            if len(starfwhms) > 0:
                seeingpixels = np.median(starfwhms)
                if forceseeingpixels:
                    if seeingpixels < 2:
                        seeingpixels = 2.01  # HAAAAAAX
            else:
                seeingpixels = peakpos
                if forceseeingpixels:
                    if seeingpixels < 2:
                        seeingpixels = 2.01  # HAAAAAAX
            seeing = seeingpixels * image['pixsize']

    elif len(fwhms) > 0:

        print "Only %i stars, using the median ..." % (len(fwhms))
        seeingpixels = np.median(fwhms)
        if forceseeingpixels:
            if seeingpixels < 2:
                seeingpixels = 2.01  # HAAAAAAX
        seeing = seeingpixels * image['pixsize']

    else:
        print "Are you kidding ? No stars at all !"
        seeing = -1.0
        seeingpixels = -1.0

    print "Measured seeing [pixels] :", seeingpixels
    print "Measured seeing [arcsec] :", seeing

    if checkplots:
        # plt.hist(fwhms, bins=np.linspace(0,10,50), facecolor='green')
        plt.hist(fwhms, bins=np.linspace(np.min(fwhms), np.max(fwhms), 50), facecolor='green')
        plt.axvline(x=seeingpixels, linewidth=2, color='red')
        plt.axvline(x=peakpos - 1.0, linewidth=2, color='blue')
        plt.axvline(x=peakpos + 1.0, linewidth=2, color='blue')
        plt.xlabel('FWHM [pixels]')
        plt.title('Histogram of FWHM')
        # plt.figtext(0.5, 0.8, r'$\mathrm{Measured\ seeing\ [pixels]\ :}\ %5.2f$'%seeingpixels)
        plt.grid(True)
        plt.show()

    # And we measure the ellipticity of the images, by looking at sources with similar width then our seeingpixels
    # Now look at this beauty : :-)
    ells = np.array([s.ell for s in sortedsexstars])
    starells = np.array([s.ell for s in sortedsexstars if abs(s.fwhm - seeingpixels) < 1.0])

    print "I found", len(ells), "stars for ellipticity measure."

    if len(starells) > 0:
        ell = np.median(starells)
    else:
        print "Bummer ! No stars for ellipticity measure."
        ell = -1.0

    print "Measured ellipticity :", ell
    if checkplots:
        plt.hist(ells, bins=np.linspace(0, 1, 50), facecolor='grey')
        plt.hist(starells, bins=np.linspace(0, 1, 50), facecolor='green')
        plt.axvline(x=ell, linewidth=2, color='red')
        plt.xlabel('Ellipticity')
        plt.title('Histogram of ellipticity')
        # plt.figtext(0.5, 0.8, r'$\mathrm{Measured\ ellipticity\ :}\ %5.2f$'%ell)
        plt.grid(True)
        plt.show()

    # New thing, we also measure the position angle of the ellipcitity
    pas = np.array([s.props["THETA_IMAGE"] for s in sortedsexstars])
    starpas = np.array([s.props["THETA_IMAGE"] for s in sortedsexstars if abs(s.fwhm - seeingpixels) < 1.0])

    if len(starpas) > 0:
        pa = np.median(starpas)
        pastd = np.std(starpas)
    else:
        pa = -1.0
        pastd = 0.0
    print "Measured position angle :", pa, pastd

    # same for the minor and major axis
    bimgs = np.array([s.props["B_IMAGE"] for s in sortedsexstars])
    starbimgs = np.array([s.props["B_IMAGE"] for s in sortedsexstars if abs(s.fwhm - seeingpixels) < 1.0])

    aimgs = np.array([s.props["A_IMAGE"] for s in sortedsexstars])
    staraimgs = np.array([s.props["A_IMAGE"] for s in sortedsexstars if abs(s.fwhm - seeingpixels) < 1.0])

    if len(starbimgs) > 0:
        bimage = np.median(starbimgs)
    else:
        bimage = -1
    print "Measured minor axis :", bimage

    if len(starbimgs) > 0:
        aimage = np.median(staraimgs)
    else:
        aimage = -1
    print "Measured major axis :", aimage

    if not checkplots:
        db.update(imgdb, ['recno'], [image['recno']],
                  {'seeing': float(seeing), 'ell': float(ell), 'goodstars': nbrstars,
                   'seeingpixels': float(seeingpixels), 'pa': float(pa), 'pastd': float(pastd), 'bimage': float(bimage),
                   'aimage': float(aimage)})

print "- " * 40

if not checkplots:
    db.pack(imgdb)

print "Done with seeing determination."
