"""
We add raw sextractor photom into the database (i.e., not normalized).
Can be run at any time once :
	- the alignment is done
	- the normalisation catalogs are written (2_runsex.py)
	
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
from config import alidir, configdir, dbbudir, imgdb, settings
from modules.kirbybase import KirbyBase
from variousfct import proquest, backupfile
from modules import star

askquestions = settings['askquestions']
sexphotomfields = settings['sexphotomfields']
sexphotomname = settings['sexphotomname']
identtolerance = settings['identtolerance']

# Selecting the images
db = KirbyBase()
if settings['update']:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], 
                              returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')
nbrofimages = len(images)

# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print("I will look for these stars :")
print("\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars]))

print("This will require the following fields :")
# Fields for the database :
dbfields = [{"name":"%s_%s_%s" % (sexphotomname, s.name, f["dbname"]), "type":f["type"]} 
                              for s in photomstars for f in sexphotomfields]
print("\n".join(["%30s : %5s" % (f["name"], f["type"]) for f in dbfields]))


dbfieldstoadd = []
for f in dbfields:
	if f["name"] not in db.getFieldNames(imgdb) :
		dbfieldstoadd.append(f)
print("I will add %i/%i fields to the database." % (len(dbfieldstoadd), len(dbfields)))

proquest(askquestions)

# As we will tweak the database, backup
backupfile(imgdb, dbbudir, 'photomdb')
	
db.addFields(imgdb, ["%s:%s" % (f["name"], f["type"]) for f in dbfieldstoadd])


for i, image in enumerate(images):
	print("- "*30)
	print(i+1, "/", nbrofimages, ":", image['imgname'])
	
	# We read the sextractor catalog :
	sexcatpath = os.path.join(alidir, image['imgname'] + ".alicat")
	sexstars = star.readsexcat(sexcatpath, maxflag = 0, posflux = False, 
                            propfields=[f["sexname"] for f in sexphotomfields])
		
	# We identify these sextractor stars with the handwritten selection
	id = star.listidentify(photomstars, sexstars, tolerance=identtolerance, 
                           onlysingle=True, verbose=True)
	
	if len(id["match"]) == 0:
		print("No stars identified, skipping this image.")
		continue
	
	updatefieldnames = []
	updatefieldvalues = []
	for s in id["match"]:
		for f in sexphotomfields:
			updatefieldnames.append("%s_%s_%s" % (sexphotomname, s.name, f["dbname"]))
			if f["type"] == "float":
				updatefieldvalues.append(float(s.props[f["sexname"]]))
			elif f["type"] == "int":
				updatefieldvalues.append(int(s.props[f["sexname"]]))
			else:
				updatefieldvalues.append(s.props[f["sexname"]])
		

	db.update(imgdb, ['recno'], [image["recno"]], updatefieldvalues, updatefieldnames)

db.pack(imgdb) # to erase the blank lines

print("Done.")
