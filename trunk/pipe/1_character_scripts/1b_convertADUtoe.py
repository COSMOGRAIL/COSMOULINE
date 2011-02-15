# 
#	This script convert the ADU level into electron level of all the images
#	You should use it right after the import of the images into the database.
#	It also define a new gain = 1 and an original gain = image gain
#


execfile("../config.py")
import glob
import pyfits
import datetime
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

print "I will convert %i images." %nbrofimages
proquest(askquestions)

backupfile(imgdb, dbbudir, "convertADUtoe")

# Check if the origin_gain is already in the database

if "origin_gain" not in db.getFieldNames(imgdb):
	db.addFields(imgdb, ['origin_gain:float'])


for i, image in enumerate(images):

	print "- " * 30
	print i+1, "/", nbrofimages, ": conversion of : ", image['imgname']
	

	# copy the actual gain and put it in the origin_gain and replace the gain by the value 1.0
	if image["origin_gain"] == None:

		filename = image['rawimg']
		origin_gain = image['gain']	# this is the orginial gain, i.e. before updating the database with the new gain of 1.0
		updatedsaturlevel = image['satur_level'] * origin_gain
		pixelarray, header = fromfits(filename)
	
		pixelarray = pixelarray * origin_gain	# so that we have an image in electron and not in ADU
	
		outfilename = os.path.join(alidir, image['imgname'] + ".fits")
		tofits(outfilename, pixelarray)			# we clean the header to avoid dangerous behaviors from iraf or sextractor

		db.update(imgdb, ['recno'], [image['recno']], [origin_gain, 1.0, updatedsaturlevel], ['origin_gain', 'gain', 'satur_level'])
		
	else:
		print "This image has already been converted."	

db.pack(imgdb)

print "Done with conversion."


