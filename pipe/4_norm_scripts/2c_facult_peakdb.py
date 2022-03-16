"""
We write an estimation of the peak value (in ADU, including sky level !)
of the photomstars into the database.
For this we have to open each image ... this is a bit slow.
"""



execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np

# Selecting the images
db = KirbyBase()
if update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')
nbrofimages = len(images)



# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print "I will look for these stars :"
print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])

print "This will require the following fields :"
# Fields for the database :
dbfields = [{"name":"%s_%s_peakadu" % (sexphotomname, s.name), "type":"float"} for s in photomstars]
print "\n".join(["%30s : %5s" % (f["name"], f["type"]) for f in dbfields])


dbfieldstoadd = []
for f in dbfields:
	if f["name"] not in db.getFieldNames(imgdb) :
		dbfieldstoadd.append(f)
print "I will add %i/%i fields to the database." % (len(dbfieldstoadd), len(dbfields))

proquest(askquestions)
# As we will tweak the database, backup

backupfile(imgdb, dbbudir, 'peakdb')
db.addFields(imgdb, ["%s:%s" % (f["name"], f["type"]) for f in dbfieldstoadd])


for i, image in enumerate(images):
	#print "- "*30
	print i+1, "/", nbrofimages, ":", image['imgname']

	(imagea, imageh) = fromfits(os.path.join(alidir, image["imgname"] + "_ali.fits"), verbose = False)
	
	updatefieldnames = []
	updatefieldvalues = []
	
	for s in photomstars:
		
		maxvalelnosky = np.max(imagea[int(round(s.x))-3:int(round(s.x))+3, int(round(s.y))-3:int(round(s.y))+3])
		peakadu = float((maxvalelnosky + image["skylevel"]) / image["gain"])
		#print s.name, peakadu

		updatefieldnames.append("%s_%s_peakadu" % (sexphotomname, s.name))
		updatefieldvalues.append(peakadu)
		

	db.update(imgdb, ['recno'], [image["recno"]], updatefieldvalues, updatefieldnames)

db.pack(imgdb) # to erase the blank lines
print "Peak measurements done."
