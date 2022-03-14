"""
Display some informations about the update you are about to run. 
Check that everything is in place before letting you run the update.
"""

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, configdir, psfnames, objcoordcats
from modules.variousfct import mterror
from modules.kirbybase import KirbyBase


update = settings['update']
refimgname_per_band = settings['refimgname_per_band']
refimgname = settings['refimgname']
allrenormsources = settings['renormsources']
objnames = settings['objnames']



print("="*25)
print("I will check your settings")

# is the update keyword set to True ?

if not update:
	raise mterror("The update keyword in your settings is set to False !")
else:
	print("update flag set to True...")

# does the database exists ?
if not os.path.isfile(imgdb):
	raise mterror("The database does not exists!!")
else:
	print("database exists...")

# is this a test ?
if settings['thisisatest']:
	mterror("'thisisatest' is set to True. Change it to False")
else:
	print("thisisatest flag set to False...")


db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo','treatme'], 
                          [True, True], 
                          returnType='dict')

#refimg exists ?
for refimg in (list(refimgname_per_band.values()) + [refimgname]):
    if not refimg in [image['imgname'] for image in images]:
    	raise mterror("The reference image does not exists !!!")
    else:
    	print(f"reference image exists: {refimg}")


# normstars exists ?
if not os.path.isfile(os.path.join(configdir, "normstars.cat")):
	raise mterror("normstars catalogue does not exists")
else:
	print("normalisation stars catalogue exists...")

# photomstars exists ?
if not os.path.isfile(os.path.join(configdir, "photomstars.cat")):
	raise mterror("photomstars catalogue does not exists")
else:
	print("photometric stars catalogue exists...")

for psfname, renormsources in zip(psfnames, allrenormsources):

    print(f"updating PSF {psfname}...")
    
    # all the needed objects are in the extraction string ?
    if not "lens" in objnames:
    	raise mterror("lens is not in the extraction catalogue!")
    for name in [elt[1] for elt in renormsources]:
    	if not name in objnames:
    		raise mterror(f"{name} is not in the extraction catalogue!")
    print("required objects will be extracted...")
    
    
    # extraction catalogues exist ?
    for objcoordcat in objcoordcats:
    	if not os.path.isfile(objcoordcat):
    		raise mterror(f"{objcoordcat} does not exists !")
    	else:
    		pass
    print("extraction catalogues exist...")
    
    
    print("*"*15)
    print("DECONVOLUTION")
