#
#	We set the medcoeff to 1.0 (if you don't want any normalization)
#	We use these medcoeffs for the f77 MCS PSF construction, to get initial values, for instance.
#

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, dbbudir, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, backupfile
askquestions = settings['askquestions']

print("We will set all medcoeffs to 1.0.")
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, 'calccoeff')

# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

# We prepare the database
if "nbrcoeffstars" not in db.getFieldNames(imgdb) :
	print("I will add some fields to the database.")
	proquest(askquestions)
	db.addFields(imgdb, ['nbrcoeffstars:int', 'maxcoeffstars:int', 'medcoeff:float', 'sigcoeff:float', 'spancoeff:float'])

for i, image in enumerate(images):
	db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': 0, 'maxcoeffstars': 0, 'medcoeff': 1.0, 'sigcoeff': 0.0, 'spancoeff': 0.0})

db.pack(imgdb)
print("Done.")
	
	
