#
#	We set the medcoeff to 1.0 (if you don't want any normalization)
#	We use these medcoeffs for the f77 MCS PSF construction, to get initial values, for instance.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from calccoeff_fct import *
from variousfct import *
import star

print "We will set all medcoeffs to 1.0."
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, 'calccoeff')

# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

# We prepare the database
if "nbrcoeffstars" not in db.getFieldNames(imgdb) :
	print "I will add some fields to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['nbrcoeffstars:int', 'maxcoeffstars:int', 'medcoeff:float', 'sigcoeff:float', 'spancoeff:float'])

for i, image in enumerate(images):
	db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': 0, 'maxcoeffstars': 0, 'medcoeff': 1.0, 'sigcoeff': 0.0, 'spancoeff': 0.0})

db.pack(imgdb)
print "Done."
	
	
