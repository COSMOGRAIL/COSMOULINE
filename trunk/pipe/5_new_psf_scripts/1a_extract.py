#
#	This is for the NEW (aka lovely psfmofsour8.txt) psf construction !
#	
#	make the sub directories of psfdir in which the psf will be build for each image
#	write the input files for the extract
#	do the extraction
#	you can relaunch these following scripts with another psfdir name in config.py !
#
#	we add also a cosmicskey, and set it to -1 meaning : cosmics detection has not run for now.
#

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
proquest(askquestions)

backupfile(imgdb, dbbudir, "extract_" + psfkey)


# Then, we inpect the current siutation.
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

	# remember where we are.
origdir = os.getcwd()

backupfile(imgdb, dbbudir, "extract_" + psfkey)


	# format the psf stars catalog
nbrpsf = len(psfstars)
psfstarstxt = ""
for psfstar in psfstars:
	psfstarstxt = psfstarstxt + "%7.2f %7.2f\n" % (psfstar['x'], psfstar['y'])
psfstarstxt = psfstarstxt.rstrip("\n") # remove the last newline

	# read the template files
extract_template = justread(extract_template_filename)



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
	
	
	# extract.txt
	
	extrdict = {"$imgname$": "in.fits", "$nbrpsf$": str(nbrpsf), "$gain$": str(image['gain']), "$stddev$": str(image['stddev'])}
	extrdict.update([["$psfstars$", psfstarstxt]])

	lenscoord = "200.00 200.00"
	extrdict.update([["$lenscoord$", lenscoord]])
	
	extracttxt = justreplace(extract_template, extrdict)
	
	extractfile = open(os.path.join(imgpsfdir, "extract.txt"), "w")
	extractfile.write(extracttxt)
	extractfile.close()
	
	os.chdir(imgpsfdir)
	os.system(extractexe)
	
	os.remove(os.path.join(imgpsfdir, "g.fits"))		# we just want the psf here.
	os.remove(os.path.join(imgpsfdir, "sig.fits"))
	
	os.remove(os.path.join(imgpsfdir, "in.fits"))
	
	os.chdir(origdir)
	
	# and we update the database with a "True" for field psfkeyflag and -1 for the cosmics detection (default value) :
	db.update(imgdb, ['recno'], [image['recno']], [True, -1], [psfkeyflag, psfcosmicskey])
	
	#os.remove(imgpsfdir + "in.fits")

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

