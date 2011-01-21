#
#	generates pngs related to the old psf construction
#

execfile("../config.py")
import shutil
from kirbybase import KirbyBase, KBError
from variousfct import *


db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['mjd'])



print "Images that you should put on the psfskiplist now :"

for i, image in enumerate(images):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	resultsdir = os.path.join(imgpsfdir, "results")
	
	if not os.path.exists(os.path.join(resultsdir, "psf_1.fits")):
		print image['imgname']
	
