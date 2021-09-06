#
#	here we do the actual geomap and gregister (pyraf)
#	we apply this inprinciple to all images gogogo, treatme, and flagali
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

# perhaps you want to tweak this to run the alignment only on a few images :

#images = db.select(imgdb, ['flagali','gogogo','treatme','maxalistars'], ['==1', True, True, '==7'], ['recno','imgname'], sortFields=['imgname'], returnType='dict')
#images = db.select(imgdb, ['flagali', 'geomaprms'], ['==1', '> 1.0'], ['recno','imgname','rotator'], returnType='dict')
#images = db.select(imgdb, ['flagali','imgname'], ['==1','c_e_20080526_35_1_1_1'], ['recno','imgname'], sortFields=['imgname'], returnType='dict')

#for image in images:
#	print image['imgname']

#recnos = [image['recno'] for image in images]
#sys.exit()


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

for i,image in enumerate(images):

    print("--------------------")
    print(i+1, "/", nbrofimages, image['imgname'])
	
    imgtorotate = os.path.join(alidir, image['imgname'] + "_skysub.fits")
    geomapin = os.path.join(alidir, image['imgname'] + ".geomap")
	
    aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
	
    if os.path.isfile(aliimg):
        "Removing existing aligned image."
        os.remove(aliimg)


    # so, we aim to replace IRAF with astroalign. First, let us
    # recover the mapped stars obtained in 1b_identcoord.py :
    referenceset, targetset = readgeomap(geomapin)
    transform, _ = aa.find_transform(referenceset, targetset)
	
	# assign the different parts of the transformation:
    geomapscale = transform.scale
    geomaprms = np.sqrt( np.sum(transform.residuals(referenceset, targetset)) / len(referenceset) )
    geomapangle = transform.rotation
    mapshifts = transform.translation
    
	
    print("Scale :", geomapscale)
    print("Angle :", geomapangle)
    print("RMS   :", geomaprms)
	
    db.update(imgdb, ['recno'], [image['recno']], {'geomapangle': geomapangle, 'geomaprms':float(geomaprms), 'geomapscale': float(geomapscale)})
    
    # apply the said transformation to the image.
    # astroalign still wants a reference to the target image: that is in case
    # it has a different shape. Thus we provide it for generality.
    
    
    
    imgtorotatedata = fits.getdata(imgtorotate)
    # aaand for some reason, this doesn't work with 32 bits data.
    aligned_image, _ = aa.apply_transform(transform, source=imgtorotatedata.astype(np.float64), 
                                                  target=refimage)
    # thus we convert it before applying the transformation, and now we
    # go back as we write the result:
    fits.writeto(aliimg, aligned_image.astype(np.float32))



db.pack(imgdb)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)


notify(computer, withsound, "Dear user, I'm done with the alignment. I did it in %s." % timetaken)

