# in this file, we're transforming the WCS header of the refimg.
# we'll use astroalign to find the transformation (translation)
# between each image and the ref image.
# THE FIRST TIME YOU RUN THIS ON A NEW DATASET, SET debug = True
# to see what kind of stars you're including. 
# (you might need to tune MINFLUX)
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import astroalign as aa
from astropy.wcs import WCS
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')

from config import alidir, dbbudir, computer, imgdb, settings, defringed
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, backupfile, nicetimediff, notify


from modules import star


askquestions = settings['askquestions']
refimgname = settings['refimgname']
maxcores = settings['maxcores']

debug = False
if debug:
    maxcores = 1
# maxcores = 1
# use debug to see what stars you are using for your alignment
# with this min flux:
MINFLUX = 500_000

def plot_debug_image(refimage, alignimg, tupleref, tuplealign, translation):
    """
    Plot a debug image showing the reference and align images with the star
    positions and their translation vectors.
    ONLY SHOWS TRANSLATIONS
    So if you have weird offsets, can be a rotation problem
    or constant offsets, a position of the reference pixel problem
    (it also has to be rotated)

    Args:
        refimage (ndarray): Reference image data.
        alignimg (ndarray): Image data to align.
        tupleref (list of tuple): Star coordinates in the reference image.
        tuplealign (list of tuple): Star coordinates in the align image.
        translation (tuple): Translation vector from astroalign.

    Returns:
        None
    """

    # Prepare subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Set vmin and vmax for consistent color scales
    vmin = min(np.nanpercentile(refimage, 0.1), np.nanpercentile(alignimg, 0.1))
    vmax = max(np.nanpercentile(refimage, 99.7), np.nanpercentile(alignimg, 99.7))

    # Plot reference image
    axes[0].imshow(refimage, cmap='gray', vmin=vmin, vmax=vmax)
    axes[0].plot([x for x, y in tupleref], [y for x, y in tupleref], 'o', mfc='None', ls='None', ms=8, color='red')
    axes[0].set_title('Reference Image')

    # Plot align image
    axes[1].imshow(alignimg, cmap='gray', vmin=vmin, vmax=vmax)
    axes[1].plot([x for x, y in tuplealign], [y for x, y in tuplealign], 'o', mfc='None', ls='None', ms=8, color='green')
    axes[1].plot([x for x, y in tupleref], [y for x, y in tupleref], 'o', mfc='None', ls='None', ms=8, color='red')
    # Add translation arrows
    for x1, y1 in tuplealign:
        axes[1].arrow(x1, y1, translation[0], translation[1], head_width=5, head_length=5, fc='blue', ec='blue')

    axes[1].set_title('Align Image')

    plt.waitforbuttonpress()

def alignImage(image, tupleref, refimage, referencewcs, cdmatrix):

    """
        input: database row, "image"


        reads the sextractor catalogue of the said image, and finds the
        transformation that aligns it to the reference catalogue.
        Then, applies this transformation to the image data.

        returns: a dictionnary containing the "flagali" flag. If flagali=1,
        additional entries (e.g. the RMS error and number of considered pairs)
        are also given in the dictionary.

        We will run this in parallel, and update the database later.
        
        btw, the cdmatrix is simply a copy of referencewcs.wcs.cd
        
        if not passed, multiprocessing weirdly doesn't work. (can't find
        the cd in the wcs object)

    """
    aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
    if os.path.exists(aliimg):
        print(f"Image {image['imgname']} already aligned.")
        return

    print("Processing", image['imgname'], "with recno", image['recno'])
    if defringed:
        imgtorotate = os.path.join(alidir, image['imgname'] + "_defringed.fits")
    else:
        imgtorotate = os.path.join(alidir, image['imgname'] + "_skysub.fits")

    # star catalogue of the image to align:
    sexcat = os.path.join(alidir, image['imgname'] + ".cat")
    autostars = star.readsexcat(sexcat, maxflag=16, posflux=True, verbose=False)
    autostars = star.sortstarlistbyflux(autostars)
    autostars = [s for s in autostars if s.flux > MINFLUX]
    tuplealign = [(s.x, s.y) for s in autostars]

    # if debug:
        # m,M = np.nanpercentile(refimage, [0.1, 99.7])
        # plt.figure()
        # plt.imshow(fits.getdata(imgtorotate), vmin=m, vmax=M)
        # xs = [s.x for s in autostars]
        # ys = [s.y for s in autostars]
        # print([s.flux for s in autostars])
        # plt.plot(xs, ys, 'o', mfc='None', ls='None', ms=8, color='red')
        # plt.title(image['imgname'])
                                                                      
        # plt.waitforbuttonpress()


    if len(autostars)<1:
        print(f"Could not align image {image['imgname']}: zero star detected.")
        return {'recno': image['recno'], 'flagali': 0}

    try:
        transform, (match1, match2) = aa.find_transform(tuplealign, tupleref)
    except aa.MaxIterError:
        print(f"Could not align image {image['imgname']}: max iterations reached before solution.")
        return {'recno': image['recno'], 'flagali': 0}
    except ValueError as VV:
        print(f"Image {image['imgname']}: error, ", VV)
        return {'recno': image['recno'], 'flagali': 0}

    if debug:
        plot_debug_image(refimage, fits.getdata(imgtorotate), match2, match1, transform.translation)
        
    # store the different parts of the transformation:
    geomapscale = transform.scale
    geomaprms = np.sqrt(np.sum(transform.residuals(match1, match2)) / len(match1))
    geomapangle = transform.rotation
    
    # ok, now we transform the WCS.
    # if the pixels are transformed actively, the coordinates must be
    # transformed the other way to compensate:
    similarity = transform.params
    invsimilarity = np.linalg.inv(similarity)
    invscalerotation = invsimilarity[:2, :2]
    invtranslation = invsimilarity[:2, 2]
    
    # copy the ref wcs and inverse transform it:
    wcs_new = referencewcs.deepcopy()
    # update the ref pixel
    refpixel = referencewcs.wcs.crpix
    # the ref pixel was actively moved to the new coordinates, so reflect
    # again gotta transform the coordinates back to point it at the same
    # sky position:
    refpixel = np.dot(invscalerotation, refpixel) + invtranslation
    # ok, put it back in the wcs
    wcs_new.wcs.crpix = refpixel
    # rotation and scaling of the cd matrix.
    wcs_new.wcs.cd = np.dot(invscalerotation, cdmatrix)
    
    # update the WCS of the target fits.
    with fits.open(imgtorotate, mode="update") as hdul:
        hdul[0].header.update(wcs_new.to_header())
        hdul.flush()

    return {'recno': image['recno'], 'geomapangle': geomapangle,
            'geomaprms': float(geomaprms),
            'geomapscale': float(geomapscale),
            'maxalistars': len(match1),
            'nbralistars': len(match1),
            'flagali': 1}



def multi_alignImage(arg):
   return alignImage(*arg)



def updateDB(db, retdict, image):
    if not retdict:
        # already aligned case, we returned nothing.
        db.update(imgdb, ['recno'], [image['recno']], {'flagali': 1})
        return
    if 'geomapscale' in retdict:
        db.update(imgdb, ['recno'], [image['recno']],
                  {'geomapangle': retdict["geomapangle"],
                   'geomaprms'  : retdict["geomaprms"],
                   'geomapscale': retdict["geomapscale"],
                   'maxalistars': retdict['maxalistars'],
                   'nbralistars': retdict['nbralistars'],
                   'flagali' : 1})
    else:
        db.update(imgdb, ['recno'], [image['recno']], {'flagali': 0})



def main():
    # As we will tweak the database, let's do a backup
    backupfile(imgdb, dbbudir, "before_alignimages_onestep")

    db = KirbyBase(imgdb)
    # get the info from the reference frame
    refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
    if len(refimage) != 1:
        print("Reference image identification problem !")
        sys.exit()
    refimage = refimage[0]
    
    
    
    # Load the WCS of the ref img (plate solved in previous script)
    refimagepath = os.path.join(alidir, refimage['imgname'] + "_skysub.fits")
    with fits.open(refimagepath) as hdul:
        wcs_ref = WCS(hdul[0].header)
        # Removing the SIP distortion information,
        wcs_ref.sip = None
        # because won't apply to other images
    
    if settings['thisisatest']:
        print("This is a test.")
        images = db.select(imgdb, ['gogogo','treatme', 'testlist'],
                                  [ True,    True,      True],
                                  ['recno','imgname'],
                                  sortFields=['imgname'],
                                  returnType='dict')
    elif settings['update']:
        print("This is an update.")
        images = db.select(imgdb, ['gogogo','treatme', 'updating'],
                                  [ True,    True,      True],
                                  ['recno','imgname'],
                                  sortFields=['imgname'],
                                  returnType='dict')
    else:
        images = db.select(imgdb, ['gogogo','treatme'],
                                  [ True,    True],
                                  ['recno','imgname'],
                                  sortFields=['imgname'],
                                  returnType='dict')

    # filter out the refimg
    images = [img for img in images if not img['imgname'] == refimgname]
    # add the useful fields:
    if "geomapangle" not in db.getFieldNames(imgdb) :
        print("I will add some fields to the database.")
        proquest(askquestions)
        db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float',
                             'geomapscale:float', 'nbralistars:int',
                             'maxalistars:int', 'flagali:int'])


    # load the reference sextractor catalog
    refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
    refautostars = star.readsexcat(refsexcat, maxflag=16, posflux=True)
    refautostars = star.sortstarlistbyflux(refautostars)
    # astroalign likes tuples, so let's simplify our star objects to (x,y) tuples:
    tupleref = [(s.x, s.y) for s in refautostars if s.flux > MINFLUX]


    nbrofimages = len(images)
    print("Number of images to treat :", nbrofimages)
    proquest(askquestions)

    starttime = datetime.now()

    # we'll still need the reference image: astroalign needs it only to
    # get the dimension of the target. Could pass the image to align itself
    # if everything has the same shape.
    refimgsuffix = '_skysub.fits'
    # (here we use the aligned image if it's an update, as the _skysub version
    #  of the ref image has probably been deleted in the initial run.)
    refimage = os.path.join(alidir, refimgname + refimgsuffix)
    refimage = fits.getdata(refimage)


    if debug:
        m,M = np.nanpercentile(refimage, [0.1, 99.7])
        plt.imshow(refimage, vmin=m, vmax=M)
        xs = [s[0] for s in tupleref]
        ys = [s[1] for s in tupleref]
        plt.plot(xs,ys, 'o', mfc='None', ls='None', ms=8, color='red')
        plt.title('ref img')
        plt.show(block=False)
    
    ### here we do the alignment in parallel.
    ###############################################################################
    ###############################################################################
    cpus = maxcores  # to avoid locally defining global variable
    if cpus == 0:
        cpus = multiprocessing.cpu_count()
    if cpus > 1 :
        pool = multiprocessing.Pool(processes=cpus)
        # very weird, I have to explicitely create an extra copy of the
        # cd matrix for this to work.  else, when using multiprocessing, the
        # wcs_ref object copy does not seem to carry the cd matrix? wtf...
        # Oh well, works with the extra copy.
        args = [(im, tupleref, refimage, wcs_ref.deepcopy(), wcs_ref.wcs.cd.copy()) for im in images]
        retdicts = pool.map(multi_alignImage, args)
    else :
        retdicts = []
        for im in images :
            print(im['imgname'])
            retdicts.append(alignImage(im, tupleref, refimage, wcs_ref, wcs_ref.wcs.cd.copy()))
    ###############################################################################
    ###############################################################################



    for i, (retdict,image) in enumerate(zip(retdicts,images)):
        updateDB(db, retdict, image)

    db.pack(imgdb)

    endtime = datetime.now()
    timetaken = nicetimediff(endtime - starttime)


    notify(computer, settings['withsound'],
           f"Dear user, I'm done with the alignment. I did it in {timetaken}.")



if __name__ == '__main__':
    main()
