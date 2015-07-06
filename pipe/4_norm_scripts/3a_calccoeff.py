"""
Calculation of first guess normalization coefficients.
You can relaunch this with other stars to test different combinations if you want.


This is a bit simplistic : here we *do* rely on the reference image as a reference.
This is well adapted to calculate such coefficients over different telescopes etc.
Of course the reference image will have a coeff of 1.0

We use FLUX_AUTO

Later we will do something more sophisticated for the renormalization.

"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np

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
normstars = star.readmancat(normstarscat)
for s in normstars:
	print s.name


print "Checking reference image ..."
refsexcat = os.path.join(alidir, refimgname + ".alicat")
refcatstars = star.readsexcat(refsexcat, propfields=["FLUX_APER", "FLUX_APER1", "FLUX_APER2", "FLUX_APER3", "FLUX_APER4"])
id = star.listidentify(normstars, refcatstars, tolerance = identtolerance)
refidentstars = id["match"]
# now refidentstars contains the same stars as normstars, but with sex fluxes.


'''
print "="*25

print refcatstars[0].props
print refcatstars[0].flux


import sys
sys.exit()
'''

if len(refidentstars) != len(normstars):
	print "Not all normstars identified in sextractor cat of reference image !"
	sys.exit()

# the maximum number of possible stars that could be used
maxcoeffstars = len(normstars)
print "Number of coefficient stars :", maxcoeffstars
nbrofimages = len(images)
print "I will treat", nbrofimages, "images."
proquest(askquestions)

def simplemediancoeff(refidentstars, identstars):
	"""
	calculates a simple (but try to get that better ... it's pretty good !) multiplicative coeff for each image
	"calc one coef for each star and take the median of them"
	coef = reference / image
	"""
	
	coeffs = []
	for refstar in refidentstars:
		for star in identstars:
			if refstar.name != star.name:
				continue
			coeffs.append(refstar.flux/star.flux)
			break
	
	coeffs = np.array(coeffs)
	if len(coeffs) > 0:
		return len(coeffs), float(np.median(coeffs)), float(np.std(coeffs)), float(np.max(coeffs) - np.min(coeffs))
	else:	
		return 0, 1.0, 99.0, 99.0
	


for i, image in enumerate(images):
	print "- "*30
	print i+1, "/", nbrofimages, ":", image['imgname']
	
	# the catalog we will read
	sexcat = os.path.join(alidir, image['imgname'] + ".alicat")
	
	# read sextractor catalog
	catstars = star.readsexcat(sexcat, maxflag = 0, posflux = True)
	if len(catstars) == 0:
		print "No stars in catalog !"
		db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': 0, 'maxcoeffstars': maxcoeffstars, 'medcoeff': 1.0, 'sigcoeff': 99.0, 'spancoeff': 99.0})
		continue
		
	# cross-identify the stars with the handwritten selection
	identstars = star.listidentify(normstars, catstars, 5.0)["match"]

	# calculate the normalization coefficient
	nbrcoeff, medcoeff, sigcoeff, spancoeff = simplemediancoeff(refidentstars, identstars)
	print "nbrcoeff :", nbrcoeff
	print "medcoeff :", medcoeff
	print "sigcoeff :", sigcoeff
	print "spancoeff :", spancoeff
	
	db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': nbrcoeff, 'maxcoeffstars': maxcoeffstars, 'medcoeff': medcoeff, 'sigcoeff': sigcoeff, 'spancoeff': spancoeff})

db.pack(imgdb) # to erase the blank lines

print "Done."
	
	
