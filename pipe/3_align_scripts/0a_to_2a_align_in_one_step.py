import numpy as np
from astropy.io import fits
import astroalign as aa

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase
from variousfct import *
import progressbar
import star

from datetime import datetime
import multiprocessing



        
def alignImage(image, tupleref, refimage):

    """
        input: database row, "image"


        reads the sextractor catalogue of the said image, and finds the
        transformation that aligns it to the reference catalogue.
        Then, applies this transformation to the image data.

        returns: a dictionnary containing the "flagali" flag. If flagali=1,
        additional entries (e.g. the RMS error and number of considered pairs)
        are also given in the dictionary.

        We will run this in parallel, and update the database later.

    """
    print("Processing", image['imgname'], "with recno", image['recno'])
    if defringed:
        imgtorotate = os.path.join(alidir, image['imgname'] + "_defringed.fits")
    else:
        imgtorotate = os.path.join(alidir, image['imgname'] + "_skysub.fits")

    # star catalogue of the image to align:
    sexcat = os.path.join(alidir, image['imgname'] + ".cat")
    autostars = star.readsexcat(sexcat, maxflag=16, posflux=True, verbose=False)
    autostars = star.sortstarlistbyflux(autostars)
    tuplealign = [(s.x, s.y) for s in autostars]

    try:
        transform, (match1, match2) = aa.find_transform(tuplealign, tupleref)
    except aa.MaxIterError:
        print(f"Could not align image {image['imgname']}.")
        return {'recno': image['recno'], 'flagali': 0}

    # assign the different parts of the transformation:
    geomapscale = transform.scale
    geomaprms = np.sqrt(np.sum(transform.residuals(match1, match2)) / len(match1))
    geomapangle = transform.rotation

    # apply the said transformation to the image.
    # astroalign still wants a reference to the target image: that is in case
    # it has a different shape. Thus we provide it for generality.
    imgtorotatedata = fits.getdata(imgtorotate)
    # aaand for some reason, this doesn't work with 32 bits data.
    aligned_image, _ = aa.apply_transform(transform,
                                          source=imgtorotatedata.astype(np.float64),
                                          target=refimage)
    # thus we convert it before applying the transformation, and now we
    # go back as we write the result:
    aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
    fits.writeto(aliimg, aligned_image.astype(np.float32), overwrite=1)

    return {'recno': image['recno'], 'geomapangle': geomapangle,
            'geomaprms': float(geomaprms),
            'geomapscale': float(geomapscale),
            'maxalistars': len(match1),
            'nbralistars': len(match1),
            'flagali': 1}



def multi_alignImage(args):
   return alignImage(*args)
   
   

def updateDB(db, retdict, image):
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

    db = KirbyBase()
    if thisisatest:
        print("This is a test.")
        images = db.select(imgdb, ['gogogo','treatme', 'testlist'],
                                  [ True,    True,      True],
                                  ['recno','imgname'],
                                  sortFields=['imgname'],
                                  returnType='dict')
    elif update:
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


    # add the useful fields:
    if "geomapangle" not in db.getFieldNames(imgdb) :
        print("I will add some fields to the database.")
        proquest(askquestions)
        db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float',
                             'geomapscale:float', 'nbralistars:int',
                             'maxalistars:int', 'flagali:int'])



    # get the info from the reference frame
    refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
    if len(refimage) != 1:
        print("Reference image identification problem !")
        sys.exit()
    refimage = refimage[0]

    # load the reference sextractor catalog
    refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
    refautostars = star.readsexcat(refsexcat, maxflag=16, posflux=True)
    refautostars = star.sortstarlistbyflux(refautostars)
    refscalingfactor = refimage['scalingfactor']
    # astroalign likes tuples, so let's simplify our star objects to (x,y) tuples:
    tupleref = [(s.x, s.y) for s in refautostars]


    nbrofimages = len(images)
    print("Number of images to treat :", nbrofimages)
    proquest(askquestions)

    starttime = datetime.now()

    # we'll still need the reference image: astroalign needs it only to
    # get the dimension of the target. Could pass the image to align itself
    # if everything has the same shape.
    refimage = os.path.join(alidir, refimgname + "_skysub.fits")
    refimage = fits.getdata(refimage)


    ### here we do the alignment in parallel.
    ###############################################################################
    ###############################################################################
    cpus = maxcores #to avoid defining locally global variable
    if cpus==0:
        cpus = multiprocessing.cpu_count()
    if cpus > 1 :
        pool = multiprocessing.Pool(processes=cpus)
        args = [(im, tupleref, refimage) for im in images]
        retdicts = pool.map(multi_alignImage, args)
    else :
        retdicts = []
        for im in images :
            retdicts.append(alignImage(im, tupleref, refimage))
    ###############################################################################
    ###############################################################################



    for i, (retdict,image) in enumerate(zip(retdicts,images)):
        updateDB(db, retdict, image)

    db.pack(imgdb)

    endtime = datetime.now()
    timetaken = nicetimediff(endtime - starttime)


    notify(computer, withsound,
           f"Dear user, I'm done with the alignment. I did it in {timetaken}.")



if __name__ == '__main__':
    main()
