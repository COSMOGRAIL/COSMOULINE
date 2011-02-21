# 
#	This script will copy the actual images, and convert them from ADU to electrons
#	You should use it right after the import of the images into the database.
#	Also we completely empty the header
#


#	 We do not update the database


execfile("../config.py")
#import glob
#import pyfits
#import datetime
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *


# selection of all the images of the database
db = KirbyBase()

if thisisatest:
	print "This is a test run!"
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict')
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)

print "I will convert %i images." % (nbrofimages)
proquest(askquestions)


for i, image in enumerate(images):
	print i+1, "/", nbrofimages, " : ", image['imgname']
	

	filename = image['rawimg']
	pixelarray, header = fromfits(filename)
	
	pixelarray = pixelarray * origin_gain	# so that we have an image in electrons and not in ADU
	
	outfilename = os.path.join(alidir, image['imgname'] + ".fits")
	tofits(outfilename, pixelarray)	# we clean the header to avoid dangerous behaviors from iraf or sextractor



db.pack(imgdb)

print "Done with conversion."


