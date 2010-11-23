# We do the same as the extract.exe, but better, and in python.


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil

db = KirbyBase()

# Something easy for warm-up :
print "Here we go for the psf construction."
print "psfkey =", psfkey
proquest(askquestions)

# Let's see if the psfstarcat exists
print "Reading psf star catalog ..."
psfstars = readmancat(psfstarcat)
print "You want to use the stars :"
for star in psfstars:
	print star['name']
	
if len(psfstars) > 4:
	raise mterror("DON'T use more then 4 stars !")
	
proquest(askquestions)

backupfile(imgdb, dbbudir, "extract_" + psfkey)


# Then, we inspect the current situation.
# Check if the psfdir already exists
if os.path.isdir(psfdir):
	print "Ok, this psfdir already exists. I will add or rebuild psfs in this set."
	print "psfdir :", psfdir
	proquest(askquestions)
	
	# Check if the psfkeyflag is in the database, to be sure it exists.
	if psfkeyflag not in db.getFieldNames(imgdb) :
		raise mterror("... but your corresponding psfkey is not in the database !")
	
	if thisisatest:
		print "This is a test !"
		print "So you want to combine/replace an existing psf with a test-run."
		proquest(askquestions)
		
		#print "You are using a testlist ! In this case I will start from scratch (i.e. delete this psfdir and psfkeyflag)."
		#proquest(askquestions)
		# we clean the directory
		#shutil.rmtree(psfdir)
		#os.mkdir(psfdir)
		# we clean the database
		#db.dropFields(imgdb, [psfkeyflag])
		#db.addFields(imgdb, ['%s:bool' % psfkeyflag])
		
	
else :
	print "I will create a NEW psf."
	print "psfdir :", psfdir
	proquest(askquestions)
	if psfkeyflag not in db.getFieldNames(imgdb) :
		db.addFields(imgdb, ['%s:bool' % psfkeyflag, '%s:int' % psfcosmicskey])
	else:
		raise mterror("... funny : this psf is already in the DB ! Please clean psfdir and psfkey !")
	os.mkdir(psfdir)

# We select the images, according to "thisisatest". Note that only this first script of the psf construction looks at this : the next ones will simply 
# look for the psfkeyflag in the database !


if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
else :
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])


print "I will treat %i images." % len(images)
proquest(askquestions)

backupfile(imgdb, dbbudir, "extract_" + psfkey)

starpositions = [
	"0:64,0:64",
	"64:128,0:64",
	"0:64,64:128",
	"64:128,64:128"
	]

for n, image in enumerate(images):
	
	print "- " * 30
	print n+1, "/", len(images), ":", image['imgname']
		
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	
	if os.path.isdir(imgpsfdir):
		print "Deleting existing stuff."
		shutil.rmtree(imgpsfdir)
	os.mkdir(imgpsfdir)
	
	# copy or link the image
	if uselinks :
		os.symlink(os.path.join(alidir, image['imgname'] + "_ali.fits"), os.path.join(imgpsfdir, "in.fits"))
	else: # copy the image
		shutil.copyfile(os.path.join(alidir, image['imgname'] + "_ali.fits"), os.path.join(imgpsfdir,"in.fits"))
	
	
	# We open this image with pyfits :
	
	
	(inarray, h) = fromfits(os.path.join(imgpsfdir, "in.fits"), hdu = 0, verbose = False)
	
	outarray = np.zeros((128, 128))
	outarraysig = outarray.copy()
	
	
	for i, star in enumerate(psfstars):
		star["xmin"] = int(star["x"]) - 33
		star["xmax"] = int(star["x"]) + 31
		star["ymin"] = int(star["y"]) - 33
		star["ymax"] = int(star["y"]) + 31
			
		star["stamp"] = inarray[star["xmin"]:star["xmax"], star["ymin"]:star["ymax"]]
		
		# sig(indice) = 1/sqrt((g(indice)/gain)+(ecart*ecart))
		star["tempsig"] = (star["stamp"]/image["gain"]) + image["stddev"]*image["stddev"]
		star["tempsig"] = np.clip(star["tempsig"], 1.0e-20, 1.0e20)
		star["stampsig"] = 1.0 / np.sqrt(star["tempsig"])

		exec("outarray[%s] = star['stamp']" % (starpositions[i]))
		exec("outarraysig[%s] = star['stampsig']" % (starpositions[i]))
		
	
	tofits(os.path.join(imgpsfdir, "g001.fits"), outarray, hdr = None, verbose = False)
	tofits(os.path.join(imgpsfdir, "sig001.fits"), outarraysig, hdr = None, verbose = False)
	
	
	
	
	
	#extrdict = {"$imgname$": "in.fits", "$nbrpsf$": str(nbrpsf), "$gain$": str(image['gain']), "$stddev$": str(image['stddev'])}
	
	#extractfile = open(os.path.join(imgpsfdir, "extract.txt"), "w")
	#extractfile.write(extracttxt)
	#extractfile.close()
	
		
	# and we update the database with a "True" for field psfkeyflag and -1 for the cosmics detection (default value) :
	db.update(imgdb, ['recno'], [image['recno']], [True, -1], [psfkeyflag, psfcosmicskey])
	

db.pack(imgdb)
	
notify(computer, withsound, "Hi there. I've extracted the PSF from %i images." % len(images))

# Now we put an alias to the ref image g001.fits, to simplify the mask creation.
if refimgname in [img["imgname"] for img in images]:
	
	imgpsfdir = os.path.join(psfdir, refimgname)
	sourcepath = os.path.join(imgpsfdir, "g001.fits")
	destpath = os.path.join(workdir, psfkey + "_ref_input.fits")
	copyorlink(sourcepath, destpath, uselinks)
	
	print "The stars extracted from the reference image are available in the workdir :"
	print destpath
	print "You can now open this file with DS9 to build your mask (optional)."
	print "Don't mask cosmics, only companion stars !"
	print "Save your region file here :"
	print os.path.join(configdir, psfkey + "_mask.reg")
	print "If asked, use physical coordinates and REG file format."
	print "You can also use this fits file to measure the fluxes of the stars,"
	print "and write these fluxes in the third col of the psfstarcat."
	
else:
	print "By the way, the reference image was not among these images !"
	print "You should always have the reference image in your selection."

