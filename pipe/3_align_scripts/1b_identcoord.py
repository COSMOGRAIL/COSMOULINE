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
import star


# Select images to treat
db = KirbyBase()
if update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo','treatme', 'updating'], [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo','treatme'], [True, True], returnType='dict')


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


# load the reference sextractor catalog
refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = star.readsexcat(refsexcat, maxflag = 16, posflux = True)
refautostars = star.sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']

# read and identify the manual reference catalog
refmanstars = star.readmancat(alistarscat) # So these are the "manual" star coordinates
id = star.listidentify(refmanstars, refautostars, tolerance = identtolerance, onlysingle = True, verbose = True) # We find the corresponding precise sextractor coordinates

if len (id["nomatchnames"]) != 0:
	print "Warning : the following stars could not be identified in the sextractor catalog :"
	print "\n".join(id["nomatchnames"])
	print "You should correct this, I stop here."
	sys.exit()
	

preciserefmanstars = star.sortstarlistbyflux(id["match"])
maxalistars = len(refmanstars)

print "I've read", len(refmanstars), "stars to use for alignment."
proquest(askquestions) 


for i,image in enumerate(images):

	print "- " * 40
	print i+1, "/", nbrofimages, ":", image['imgname']
	scalingfactor = image['scalingfactor']
	scalingratio = refscalingfactor/scalingfactor
	print "scalingratio :", scalingratio
	
	sexcat = os.path.join(alidir, image['imgname'] + ".cat")
	autostars = star.readsexcat(sexcat, maxflag = 16, posflux = True)
	autostars = star.sortstarlistbyflux(autostars) # crucial !

	geomapin = os.path.join(alidir, image['imgname'] + ".geomap")

	
	trans = star.findtrans(preciserefmanstars, autostars, scalingratio = scalingratio, tolerance = identtolerance, minnbrstars = identminnbrstars, mindist = identfindmindist, nref = 10, nauto = 50, verbose=True)

	if trans["nbrids"] < 0:
		db.update(imgdb, ['recno'], [image['recno']], {'flagali': 0, 'nbralistars': 0})
		print "I'll have to skip this one ...\n"
		continue

	pairs = star.formpairs(preciserefmanstars, autostars, tolerance = identtolerance, onlysingle = True, transform = True, scalingratio = scalingratio, angle = trans["angle"], shift = trans["shift"], verbose = True)

	# We build a comment string about the non matching stars :
	comment = []
 	if len(pairs["nomatch"]) > 0 :
 		comment.append("No match :")
 		for s in pairs["nomatch"]:
 			comment.append(" " + s.name)
 		comment.append(" ")
 	if len(pairs["notsure"]) > 0 :
 		comment.append("Not sure :")
 		for s in pairs["notsure"]:
 			comment.append(" " + s.name)
 	comment = "".join(comment)
	print "Comment :", comment
		
	
	nbralistars = len(pairs["idlist1"])
	print "nbralistars :", nbralistars	
	db.update(imgdb, ['recno'], [image['recno']], {'flagali': 1, 'nbralistars': nbralistars, 'maxalistars': maxalistars, 'alicomment':comment, 'angle':trans["angle"]})
	
	# We write the input file for the iraf geomap task
	# "xref yref x y"
	# we have a function to do this in star :
	
	star.writeforgeomap(geomapin, zip(pairs["idlist1"], pairs["idlist2"]))
	print "Done"

print "- " * 40

db.pack(imgdb) # to erase the blank lines

	
	
	
	
