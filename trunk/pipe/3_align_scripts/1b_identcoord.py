#
#	Script to find the rotation and shift for each image
#	so that it matches the choosen reference frame.
#	As a result, the input files to geomap are written, containing
#	the corresponding coordinates of the choosen alignment stars in
#	each image.
#
#	Here we do arbitrary rotation ! And we do not care about any center anymore
#	All rotation are around (0,0)
#
#	We will add a special flagali to the database to describe how it went.
#	all images with flagali = 1 can then be aligned
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from star import *

# - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Some parameters to tweak the identification :

findtolerance = 5.0	# error (in pixels) for star identification when finding the shift and rotation
			# 5.0 should work (even 2.0 does), put higher values if you have strong distortion (maybe 20.0 ?)
findminnbrstars = 5	# number of stars that must match for the finding to be sucessfull
			# a default value would be half of the number of alignment stars for instance.
			# minimum is 3 of course
			# A small number will give higher probability of wrong alignment, if the field is rich and tolerance high...
findmindist = 200	# distances (in pixels) of stars to consider for finding pairs in the algorithm
			# 200 pixels is good. Put smaller values if you have only a few close stars for alignment.

pairstolerance = findtolerance # Keep it like this, it's simpler.

# - - - - - - - - - - - - - - - - - - - - - - - - - - 



# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')

# you can tweak this if you want to rerun the script on not-yet aligned images only ...
#images = db.select(imgdb, ['gogogo','treatme','flagali'], [True, True,'!=1'], returnType='dict')

nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)


# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, "identcoord")

# Prepare database : add new fields
if "flagali" not in db.getFieldNames(imgdb) :
	print "I will add some fields to the database."
	proquest(askquestions)
	db.addFields(imgdb, ['flagali:int', 'nbralistars:int', 'maxalistars:int', 'angle:float', 'alicomment:str'])


# get the info from the reference frame
refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
if len(refimage) != 1:
	print "Reference image identification problem !"
	sys.exit()
refimage = refimage[0]

# We make a link to the reference image, in the alidir.
# That's usefull for human softies only. Real computers don't need such stuff.
#curdir = os.getcwd()
#os.chdir(alidir)
#fullrefimgname = refimgname + ".fits"
#linkname = "ref.fits"
#if os.path.isfile(linkname):
#	os.remove(linkname)
#os.symlink(fullrefimgname, linkname)
#os.chdir(curdir)


# load the reference sextractor catalog
refsexcat = alidir + refimage['imgname'] + ".cat"
refautostars = readsexcatasstars(refsexcat)
refautostars = sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']

# read and identify the manual reference catalog
refmanstars = readmancatasstars(alistarscat)
preciserefmanstars = listidentify(refmanstars, refautostars, 3.0)
preciserefmanstars = sortstarlistbyflux(preciserefmanstars)
maxalistars = len(refmanstars)

print "I've read", len(refmanstars), "stars to use for alignment."
proquest(askquestions) 

if len(preciserefmanstars) != len(refmanstars):
	print "Could not identify all the alignment stars in the sextractor catalog of ref image..."
	sys.exit()



for i,image in enumerate(images):

	print "- " * 40
	print i+1, "/", nbrofimages, ":", image['imgname']
	scalingfactor = image['scalingfactor']
	scalingratio = refscalingfactor/scalingfactor
	print "scalingratio :", scalingratio
	
	sexcat = alidir + image['imgname'] + ".cat"
	autostars = readsexcatasstars(sexcat)
	autostars = sortstarlistbyflux(autostars) # crucial for speed !
	
	geomapin = alidir + image['imgname'] + ".geomap"
	
	
	#autostars[0].write()
	#autostars[1].write()
	#zoomstarlist(autostars, scalingratio)
	#autostars[0].write()
	#autostars[1].write()
	
	#sys.exit()
	
	(flag, foundangle, foundshift) = findtrans(autostars, preciserefmanstars, scalingratio, tolerance = findtolerance,  minnbrstars = findminnbrstars,  mindist = findmindist)
	
	if flag < 0:
		db.update(imgdb, ['recno'], [image['recno']], {'flagali': 0, 'nbralistars': 0})
		print "I'll have to skip this one ...\n"
		continue

	# transform all these autostars to match the manual
	# alignment selection of the reference
	
	#rotatestarlist(autostars, foundangle, (0, 0))
	#shiftstarlist(autostars, foundshift)
	
	(comment, pairs) = formpairs(preciserefmanstars, autostars, foundangle, foundshift, scalingratio, tolerance = pairstolerance)
	print "Comment :", comment
		
	
	nbralistars = len(pairs)
	print "nbralistars :", nbralistars	
	db.update(imgdb, ['recno'], [image['recno']], {'flagali': 1, 'nbralistars': nbralistars, 'maxalistars': maxalistars, 'alicomment':comment, 'angle':foundangle})
	
	# write the input file for the iraf geomap task
	# "xref yref x y"
	writeforgeomap(geomapin, pairs)
	print "Done"

print "- " * 40

db.pack(imgdb) # to erase the blank lines

	
	
	
	
