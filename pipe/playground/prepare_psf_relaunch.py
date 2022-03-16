
#	You stopped a PSF (new version) construction by killing the script 2_psf.py
#	Now you have a mess : extraction and replacenan is done for all, but some PSFs are not done.
#	This script unsets the treatmeflag for all PSFs that have been built, so that you can 
#	relaunch the 2_psf.py on those images not yet done.
#	It's quite robust to tweak, but it is slow !

#----------

nbr_if_done = 15	# Number of files in the PSF dirs if the PSF has been done

# A list of images to redo anyway (typically the image that was in process when you killed the script ...)
imgstoredoanyway = ["Mer2_qk270885"]

#----------



exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *


print("Please edit the source before running me.")
proquest(askquestions)

backupfile(imgdb, dbbudir, "prepare_psf_relaunch")
db = KirbyBase()


origdir = os.getcwd()

images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict')


print("I will check %i images." % len(images))
print("The psfdir :")
print(psfdir)
proquest(askquestions)


nchanged = 0

for image in images:

	imgpsfdir = psfdir + image['imgname'] + "/"

	file_count = len(os.walk(imgpsfdir).next()[2])
	#print file_count
	
	if (file_count == nbr_if_done) and (image['imgname'] not in imgstoredoanyway):
		print(image['imgname'], "is done.")
		nchanged += 1
		db.update(imgdb, ['imgname'], [image['imgname']], [False], ['treatme'])
	else:
		print(image['imgname'])

	

db.pack(imgdb)

print("I've set treatme to False for", nchanged, "images.")
print(len(images) - nchanged, "images remain to be done.")

print("Don't forget to put treatme to True again once you are done !")



