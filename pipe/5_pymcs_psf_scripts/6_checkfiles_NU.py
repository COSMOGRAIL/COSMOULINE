#
#	generates pngs related to the old psf construction
#

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
import shutil
from kirbybase import KirbyBase, KBError
from variousfct import *


db = KirbyBase()
if update:
	images = db.select(imgdb, ['gogogo','treatme', 'updating',psfkeyflag], [True,True,True, True], returnType='dict', sortFields=['mjd'])

else:
	images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['mjd'])


print("Images that I on the psfskiplist now :")
skiplist = open(psfkicklist, "a")
for i, image in enumerate(images):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	resultsdir = os.path.join(imgpsfdir, "results")
	
	if not os.path.exists(os.path.join(resultsdir, "psf_1.fits")):
		print(image['imgname'])
		skiplist.write("\n" + image["imgname"])
skiplist.close()