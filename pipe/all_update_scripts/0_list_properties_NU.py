"""
Display some informations about the update you are about to run. Check that everything is in place before letting you run the update.
"""

execfile('../config.py')
import os, sys
from variousfct import *
from kirbybase import KirbyBase, KBError

print "="*25
print "I will check your settings"

# is the update keyword set to True ?

if not update:
	raise mterror("The update keyword in your settings is set to False !")
else:
	print "update flag set to True..."

# does the database exists ?
if not os.path.isfile(imgdb):
	raise mterror("The database does not exists !! How can you update something that does not exists ?")
else:
	print "database exists..."

# is this a test ?
if thisisatest:
	mterror("The flag thisisatest is set to True. Change it to False")
else:
	print "thisisatest flag set to False..."


db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

#refimg exists ?
if not refimgname in [image['imgname'] for image in images]:
	raise mterror("The reference image does not exists !!!")
else:
	print "reference image exists..."


# alistars exists ?
if not os.path.isfile(os.path.join(configdir, "alistars.cat")):
	raise mterror("alistars catalogue does not exists")
else:
	print "alignment stars catalogue exists..."

# normstars exists ?
if not os.path.isfile(os.path.join(configdir, "normstars.cat")):
	raise mterror("normstars catalogue does not exists")
else:
	print "normalisation stars catalogue exists..."

# photomstars exists ?
if not os.path.isfile(os.path.join(configdir, "photomstars.cat")):
	raise mterror("photomstars catalogue does not exists")
else:
	print "photometric stars catalogue exists..."


print "updating PSF %s..."  % psfname

# all the needed objects are in the extraction string ?
if not "lens" in objnames:
	raise mterror("lens is not in the extraction catalogue!")
for name in [elt[1] for elt in renormsources]:
	if not name in objnames:
		raise mterror("%s is not in the extraction catalogue!" % name)
print "required objects will be extracted..."


# extraction catalogues exist ?
for objcoordcat in objcoordcats:
	if not os.path.isfile(objcoordcat):
		raise mterror("%s does not exists !" % objcoordcat)
	else:
		pass
print "extraction catalogues exist..."


print "*"*15
print "DECONVOLUTION"
