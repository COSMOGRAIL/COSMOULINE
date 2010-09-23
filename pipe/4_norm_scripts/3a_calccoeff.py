#
#	We read the "normstars.tab" file and identify the corresponding stars,
#	write the good stars with their measured fluxes (various techniques and fluxerrors) into one textfile for
#	each image.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from calccoeff_fct import *
from variousfct import *
from star import *

	# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, 'calccoeff')

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')
#images = db.select(imgdb, ['imgname'], ['MaiSITE1_oa100163'], returnType='dict')

# we prepare the database
if "nbrcoeffstars" not in db.getFieldNames(imgdb) :
	print "I will add some fields to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['nbrcoeffstars:int', 'maxcoeffstars:int', 'medcoeff:float', 'sigcoeff:float', 'spancoeff:float'])


# we read the handwritten star catalog
normstars = readmancatasstars(normstarscat)

print "Checking reference image ..."
refsexcat = alidir + refimgname + ".alicat"
refcatstars = readsexcatasstars(refsexcat)
refidentstars = listidentify(normstars, refcatstars, 5.0)
# now refidentstars contains the same stars as normstars, but with sex fluxes.


if len(refidentstars) != len(normstars):
	print "Not all normstars identified in sextractor cat of reference image !"
	sys.exit()

# the maximum number of possible stars that could be used
maxcoeffstars = len(normstars)
print "Number of coefficient stars :", maxcoeffstars
nbrofimages = len(images)
print "I will treat", nbrofimages, "images."
proquest(askquestions)


for i, image in enumerate(images):
	print "- "*30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
	# the catalog we will read
	sexcat = alidir + image['imgname'] + ".alicat"
	
	# read sextractor catalog
	catstars = readsexcatasstars(sexcat)
	if len(catstars) == 0:
		print "No stars in catalog !"
		db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': 0, 'maxcoeffstars': maxcoeffstars, 'medcoeff': 1.0, 'sigcoeff': 99.0, 'spancoeff': 99.0})
		continue
		
	# cross-identify the stars with the handwritten selection
	identstars = listidentify(normstars, catstars, 5.0)

	# calculate the normalization coefficient
	nbrcoeff, medcoeff, sigcoeff, spancoeff = simplemediancoeff(refidentstars, identstars)
	print "nbrcoeff :", nbrcoeff
	print "medcoeff :", medcoeff
	print "sigcoeff :", sigcoeff
	print "spancoeff :", spancoeff
	
	db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': nbrcoeff, 'maxcoeffstars': maxcoeffstars, 'medcoeff': medcoeff, 'sigcoeff': sigcoeff, 'spancoeff': spancoeff})

db.pack(imgdb) # to erase the blank lines

print "Done."
	
	
