#
#    here we do the actual geomap and gregister (pyraf)
#    we apply this inprinciple to all images gogogo, treatme, and flagali
#


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
import numpy as np
from astropy.io import fits
import astroalign as aa

from kirbybase import KirbyBase, KBError
import math
# from pyraf import iraf
from variousfct import *
from datetime import datetime, timedelta
import progressbar
import multiprocessing

from star import readgeomap

# As we will tweak the database, let's do a backup
backupfile(imgdb, dbbudir, "alignimages")

db = KirbyBase()
if thisisatest:
    print("This is a test.")
    images = db.select(imgdb, ['flagali','gogogo','treatme', 'testlist'], ['==1',True, True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')
elif update:
    print("This is an update.")
    images = db.select(imgdb, ['flagali','gogogo','treatme', 'updating'], ['==1',True, True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')
    askquestions = False
else:
    images = db.select(imgdb, ['flagali','gogogo','treatme'], ['==1',True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')




if "geomapangle" not in db.getFieldNames(imgdb) :
    print("I will add some fields to the database.")
    proquest(askquestions)
    db.addFields(imgdb, ['geomapangle:float', 'geomaprms:float', 'geomapscale:float'])

nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)

starttime = datetime.now()

# we'll still need the reference image, see below.
refimage = fits.getdata(db.select(imgdb, ['imgname'], [refimgname], returnType='dict')[0]['rawimg'])


def alignImage(image):
    try:
        print("Processing", image['imgname'], "with recno", image['recno'])
        imgtorotate = os.path.join(alidir, image['imgname'] + "_skysub.fits")
        geomapin = os.path.join(alidir, image['imgname'] + ".geomap")
        
        aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
        
    
        # so, we aim to replace IRAF with astroalign. First, let us
        # recover the mapped stars obtained in 1b_identcoord.py :
        referenceset, toalignset = readgeomap(geomapin)
        
        # now this might fail if one of the images is e.g. distorted.
        # thus wrap the find_transform operation in a try/except block.
        transform, _ = aa.find_transform(toalignset, referenceset)

        
        # assign the different parts of the transformation:
        geomapscale = transform.scale
        geomaprms   = np.sqrt( np.sum(transform.residuals(toalignset, referenceset)) / len(referenceset) )
        geomapangle = transform.rotation
        mapshifts   = transform.translation
        
        print('transforming image no. ', image['recno'])
        # apply the said transformation to the image.
        # astroalign still wants a reference to the target image: that is in case
        # it has a different shape. Thus we provide it for generality.
        imgtorotatedata  = fits.getdata(imgtorotate)
        # aaand for some reason, this doesn't work with 32 bits data.
        aligned_image, _ = aa.apply_transform(transform, 
                                              source=imgtorotatedata.astype(np.float64), 
                                              target=refimage)
        # thus we convert it before applying the transformation, and now we
        # go back as we write the result:
        fits.writeto(aliimg, aligned_image.astype(np.float32), overwrite=1)
    except:
        print(f"Could not align image {image['imgname']}.")
        return {'recno':image['recno'], 'flagali':0}
    
    return {'recno': image['recno'], 'geomapangle': geomapangle, 
            'geomaprms':float(geomaprms), 
            'geomapscale': float(geomapscale)}
   
msg  = "Sorry to interrupt: do you want to run this in parallel?"
msg += f"\ntype yes to run on {maxcores} cores, anything else to run in serial: "
resp = input(msg)

if resp.lower() == "yes":
    pool = multiprocessing.Pool(processes=maxcores)
    retdicts = pool.map(alignImage, images)
else:
    retdicts = []
    for image in images:
        retdicts.append(alignImage(image))



widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(images)).start()
for i, (retdict,image) in enumerate(zip(retdicts,images)):
    if not retdict == None:
        if 'geomapscale' in retdict:
            db.update(imgdb, ['recno'], [image['recno']], 
                      {'geomapangle': retdict["geomapangle"], 
                       'geomaprms': retdict["geomaprms"], 
                       'geomapscale': retdict["geomapscale"]})
        else:
            db.update(imgdb, ['recno'], [image['recno']], {'flagali':0})
    pbar.update(i)
pbar.finish()    


db.pack(imgdb)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)


notify(computer, withsound, "Dear user, I'm done with the alignment. I did it in %s." % timetaken)

