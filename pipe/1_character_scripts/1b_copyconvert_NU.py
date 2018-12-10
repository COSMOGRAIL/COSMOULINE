# 
#	This script will copy the actual images, and convert them from ADU to electrons
#	You should use it right after the import of the images into the database.
#	Also we completely empty the header
#


#	 We do not update the database


execfile("../config.py")
redofromscratch = False

from kirbybase import KirbyBase, KBError
from variousfct import *

db = KirbyBase()

if thisisatest:
	print "This is a test run!"
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict')
elif update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)

print "I will copy/convert %i images." % (nbrofimages)
proquest(askquestions)


for i, image in enumerate(images):
	
	# check if file exists
	print image['imgname']
	outfilename = os.path.join(alidir, image['imgname'] + ".fits")
	print i+1, "/", nbrofimages, " : ", image['imgname'], ", gain = %.3f" % (image['gain'])
	if not redofromscratch:
		if os.path.isfile(outfilename):
			print "Image already exists. I skip..."
			#pass
			continue
	
	pixelarray, header = fromfits(image['rawimg'])
	
	pixelarray = pixelarray * image['gain']	# so that we have an image in electrons and not in ADU
		
	tofits(outfilename, pixelarray)	# we clean the header to avoid dangerous behaviors from iraf or sextractor

#db.pack(imgdb)

print "Done with copy/conversion."


