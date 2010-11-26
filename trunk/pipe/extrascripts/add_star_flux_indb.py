#	
#	A script to add into the database the sextractor aperture flux of a specific star
#	You need a catalog that contains the coordinates of the star (You could use the same one than for the extraction "obj_key.cat")



execfile("../config.py")
from kirbybase import KirbyBase, KBError
from calccoeff_fct import *
from variousfct import *
from star import *
import os

#---- Here is the only parameter you have to tweak ---------

startoadd = "lens"		# specify the name of the star here

#----------------------------------------------------------

print "This script is to add the sextractor aperture flux of a specific star... adapt the source !"
proquest(askquestions)


print "I will add the flux of star %s in the database."	%startoadd
proquest(askquestions)

	# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, 'add_star_flux_%s' %startoadd)

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')


# we prepare the database
newfield = "flux_sex_%s" %startoadd
if newfield not in db.getFieldNames(imgdb) :
	print "I will add a field to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['%s:float'%newfield])

# we read the handwritten star catalog
starcat = os.path.join(configdir, "obj_%s.cat" %startoadd)
objcoords = readmancatasstars(starcat)
if len(objcoords) != 1 : raise mterror("Oh boy ... one star at a time please !")


for i, image in enumerate(images):
	print "- "*30
	print i+1, "/", len(images), ":", image['imgname']
	
	
	# the catalog we will read
	sexcat = alidir + image['imgname'] + ".alicat"
	
	# read sextractor catalog
	catstars = readsexcatasstars(sexcat)
	if len(catstars) == 0:
		print "No stars in catalog !"
		db.update(imgdb, ['recno'], [image['recno']], {newfield: 0.0})
		continue
		
	# cross-identify the stars with the handwritten selection
	identstars = listidentify(objcoords, catstars, 5.0)
	
	print 'star flux : ', identstars[0].flux
	db.update(imgdb, ['recno'], [image['recno']], {newfield: identstars[0].flux})

db.pack(imgdb) # to erase the blank lines

print "Done."
