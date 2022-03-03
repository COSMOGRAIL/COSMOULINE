#
#	generates pngs related to the old psf construction
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
from config import settings, psfkeyflag, imgdb, psfkicklist, psfdir
from modules.kirbybase import KirbyBase


db = KirbyBase(imgdb)
if settings['update']:
	images = db.select(imgdb, ['gogogo','treatme', 'updating', psfkeyflag], 
                              [True,True,True, True], 
                              returnType='dict', sortFields=['mjd'])

else:
	images = db.select(imgdb, ['gogogo','treatme', psfkeyflag], 
                              [True,True,True], 
                              returnType='dict', sortFields=['mjd'])


print("Images that I have on the psfskiplist now :")
with open(psfkicklist, "a") as skiplist:
    for i, image in enumerate(images):
    
    	imgpsfdir = os.path.join(psfdir, image['imgname'])
    	resultsdir = os.path.join(imgpsfdir, "results")
    	
    	if not os.path.exists(os.path.join(resultsdir, "psf_1.fits")):
    		print(image['imgname'])
    		skiplist.write("\n" + image["imgname"])
