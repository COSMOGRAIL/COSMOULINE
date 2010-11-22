#
#	THIS IS FOR THE "OLD" DECONVOLUTION PROGRAMS !
#
#	obsds20, "psf.exe"
#	

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil

origdir = os.getcwd()

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme', psfkeyflag], [True, True, True], returnType='dict')


print "Images for which the psf construction has failed :"
	
for image in images:
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	
	if not os.path.isfile(os.path.join(imgpsfdir, "mofc.fits")):
		print image['imgname']
	
print "Done."
	
	
