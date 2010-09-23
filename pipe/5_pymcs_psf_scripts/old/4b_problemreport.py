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

	
for image in images:
	imgpsfdir = psfdir + image['imgname'] + "/"
	
	if not os.path.isfile(imgpsfdir + "mofc.fits"):
		print image['imgname']
	
print "Done."
	
	
