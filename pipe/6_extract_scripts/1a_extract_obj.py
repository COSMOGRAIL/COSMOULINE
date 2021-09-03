#	
#	this script is here to just extract the object to deconvolve
#	it uses the new extract.exe programm, but I separateted this from the psf construction.
#	So I will throw away psf extraction.
#	
#	the important think here is objkey !	
#
#	Again, this script is a bit long, as it performs some checks
#	to make sure that the dear user does not make mistakes.
#


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil


db = KirbyBase()

print("objkey =", objkey)
	
# read the position of the object to extract

objcoords = readmancat(objcoordcat)
if len(objcoords) != 1 : raise mterror("Oh boy ... one extraction at a time please !")
# We do not care about the name that you gave to this source...
# In fact we do not care about the source at all, just want to know what part of the image to extract.
#print "name = ", objcoords[0]['name']
objcoordtxt = "%7.2f %7.2f\n" % (objcoords[0]['x'], objcoords[0]['y'])
print("coords = ", objcoordtxt)
proquest(askquestions)


# select images to extract from
db = KirbyBase()

if thisisatest :
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])

nbrofimages = len(images)

print("I will extract from", nbrofimages, "images.")
print("Please understand that I update the database.")
print("Thus, do not run me in parallel !")
proquest(askquestions)

# Before any change, we backup the database.
backupfile(imgdb, dbbudir, "extract_"+objkey)


# We check if this obj already exists :

if os.path.isdir(objdir):	# start from empty directory
	print("Ok, this objdir already exists :")
	print(objdir)
	
	if objkeyflag not in db.getFieldNames(imgdb) :
		raise mterror("... but your corresponding objkey is not in the database !")
	
	print("I will add or rebuild images within this objdir.")
	proquest(askquestions)
else :
	
	print("I will create a NEW objdir/objkey !")
	print(objdir)
	proquest(askquestions)
	if objkeyflag not in db.getFieldNames(imgdb) :
		db.addFields(imgdb, ['%s:bool' % objkeyflag, '%s:int' % objcosmicskey])
	else:
		raise mterror("... funny : the objkey was in the DB ! Please clean objdir and objkey !")
	os.mkdir(objdir)
	


	# read the template files
extract_template = justread(extract_template_filename)

origdir = os.getcwd()
n = 0
for image in images:
	n +=1
	print(n, "/", len(images), ":", image['imgname'])

	
	imgobjdir = os.path.join(objdir, image['imgname'])
	
	if os.path.isdir(imgobjdir):
		print("Deleting existing stuff.")
		shutil.rmtree(imgobjdir)
	os.mkdir(imgobjdir)
	
	os.symlink(os.path.join(alidir, image['imgname'] + "_ali.fits") , os.path.join(imgobjdir, "in.fits"))
	
	# extract.txt
	
	extrdict = {"$imgname$": "in.fits", "$nbrpsf$": "1", "$gain$": str(image['gain']), "$stddev$": str(image['stddev'])}
	extrdict.update([["$psfstars$", "200.0 200.0"]])
	extrdict.update([["$lenscoord$", objcoordtxt]])
	
	extracttxt = justreplace(extract_template, extrdict)
	
	extractfile = open(os.path.join(imgobjdir, "extract.txt"), "w")
	extractfile.write(extracttxt)
	extractfile.close()
	
	os.chdir(imgobjdir)
	os.system(extractexe)
	os.remove("g001.fits")		# we remove the one psf we have extracted
	os.remove("sig001.fits")
	os.chdir(origdir)
	
	if os.path.exists(os.path.join(imgobjdir, "in.fits")):
		os.remove(os.path.join(imgobjdir, "in.fits"))
	
	# and we update the database with a "True" for field psfkeyflag :
	db.update(imgdb, ['recno'], [image['recno']], [True, -1], [objkeyflag, objcosmicskey])
	
db.pack(imgdb)

notify(computer, withsound, "Master, I've extracted a source from %i images."%n)


if refimgname in [img["imgname"] for img in images]:
	
	imgobjdir = os.path.join(objdir, refimgname)
	sourcepath = os.path.join(imgobjdir, "g.fits")
	destpath = os.path.join(workdir, objkey + "_ref_input.fits")
	copyorlink(sourcepath, destpath, uselinks)
	
	print("I have linked the extraction from the reference image here :")
	print(destpath)	
else:
	print("Warning : the reference image was not in your selection !")


