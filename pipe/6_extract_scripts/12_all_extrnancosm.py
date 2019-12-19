# I extract according to objkey, replace NAN, and find cosmics.
# All in one script.
# The database update is done right at the beginning, i.e.
# no need to wait that I'm done before launching the next scripts
# that modify the db.

# On some computers, it is more efficient to have serial extractions
# instead of parallell, especially if your IO flow is slow
# In that case, use the present script.
# It is a simple loop on the original 12_extrnancosm.py




execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil
import progressbar
import astropy.io.fits as pyfits
import cosmics

# I could try to be smarter, and extract only the stars needed for the renormalisation...
# Nah, it weights barely nothing (less than 100Mb for 1000 images).
if update:
	askquestions=False

print "I will extract, replace NaN, and mask cosmics for the following sources:"
for objkey, objdir, objkeyflag, objcosmicskey, objcoordcat in zip(objkeys, objdirs, objkeyflags, objcosmicskeys, objcoordcats):

	print "objkey =", objkey
	# read the position of the object to extract
	objcoords = readmancat(objcoordcat)
	if len(objcoords) != 1 : raise mterror("Oh boy ... one extraction at a time please !")
	# We do not care about the name that you gave to this source...
	# In fact we do not care about the source at all, just want to know what part of the image to extract.
	#print "name = ", objcoords[0]['name']
	objcoordtxt = "%7.2f %7.2f\n" % (objcoords[0]['x'], objcoords[0]['y'])
	print "Source name = ", objcoords[0]['name']
	print "coords = ", objcoordtxt

print "Warning, no further questions will be asked beyond this one"
proquest(askquestions)
print "This may take some time..."

askquestions = False

for objkey, objdir, objkeyflag, objcosmicskey, objcoordcat in zip(objkeys, objdirs, objkeyflags, objcosmicskeys, objcoordcats):

	db = KirbyBase()
	print "objkey =", objkey

	# read the position of the object to extract

	objcoords = readmancat(objcoordcat)
	if len(objcoords) != 1 : raise mterror("Oh boy ... one extraction at a time please !")
	# We do not care about the name that you gave to this source...
	# In fact we do not care about the source at all, just want to know what part of the image to extract.
	#print "name = ", objcoords[0]['name']
	objcoordtxt = "%7.2f %7.2f\n" % (objcoords[0]['x'], objcoords[0]['y'])

	print "Source name (I don't use it, just for you to check) = ", objcoords[0]['name']
	print "coords = ", objcoordtxt

	proquest(askquestions)


	# select images to extract from
	db = KirbyBase()

	if thisisatest :
		print "This is a test run."
		images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	elif update:
		print "This is an update."
		images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	else :
		images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])

	nbrofimages = len(images)

	print "I will extract, replace NaN, and mask cosmics on ", nbrofimages, "images."


	print "I will start by updating the database."
	print "Thus, wait for this progressbar to be done before launching e.g. another extraction."
	proquest(askquestions)


	if os.path.isdir(objdir):	# start from empty directory
		print "Ok, this objdir already exists :"
		print objdir

		if objkeyflag not in db.getFieldNames(imgdb) :
			raise mterror("... but your corresponding objkey is not in the database !")

		print "I will add or rebuild images within this objdir."
		proquest(askquestions)
	else :

		print "I will create a NEW objdir/objkey !"
		print objdir
		proquest(askquestions)
		if objkeyflag not in db.getFieldNames(imgdb) :
			db.addFields(imgdb, ['%s:bool' % objkeyflag, '%s:int' % objcosmicskey])
		else:
			raise mterror("... funny : the objkey was in the DB ! Please clean objdir and objkey !")
		os.mkdir(objdir)


	# Now we prepare the database.

	# Before any change, we backup the database.
	backupfile(imgdb, dbbudir, "extract_"+objkey)

	widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
	pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(images)).start()

	for i, image in enumerate(images):
		pbar.update(i)
		db.update(imgdb, ['recno'], [image['recno']], [True, -1], [objkeyflag, objcosmicskey])
	pbar.finish()

	# As usual, we pack the db :
	db.pack(imgdb)


	notify(computer, withsound, "Ok, done with updating the database !")
	print "If the rest of this script fails somehow, it might be safe to go on from the last db backup."


		# read the template files
	extract_template = justread(extract_template_filename)

	origdir = os.getcwd() # Is used by all steps !

	for i, image in enumerate(images):
		print "Extraction %s %i/%i : %s" % (objkey, i+1, len(images), image["imgname"])

		imgobjdir = os.path.join(objdir, image['imgname'])

		if os.path.isdir(imgobjdir):
			print "Deleting existing stuff."
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


	print "Done with extraction."

	if refimgname in [img["imgname"] for img in images]:

		imgobjdir = os.path.join(objdir, refimgname)
		sourcepath = os.path.join(imgobjdir, "g.fits")
		destpath = os.path.join(workdir, objkey + "_ref_input.fits")
		copyorlink(sourcepath, destpath, uselinks)

		print "I have linked the extraction from the reference image here :"
		print destpath
	else:
		if not update:
			print "Warning : the reference image was not in your selection !"



	# Now the NaN :

	def isNaN(x):
		return x!=x

	def replaceNaN(filename, value):
		sigstars = pyfits.open(filename, mode='update')
		scidata = sigstars[0].data
		if True in isNaN(scidata):
			print "Yep, some work for me : ", len(scidata[isNaN(scidata)]), "pixels."
		scidata[isNaN(scidata)] = value
		sigstars.flush()

	def replacezeroes(filename, value):
		myfile = pyfits.open(filename, mode='update')
		scidata = myfile[0].data
		for x in range(len(scidata)):
			for y in range(len(scidata[0])):
				if scidata[x][y] < 1.0e-8:
					print "Nearly zero at ", x, y
					scidata[x][y] = value
		myfile.flush()


	for i, image in enumerate(images):
		print "NaN replacement %s %i/%i : %s" % (objkey, i+1, len(images), image["imgname"])

		imgobjdir = os.path.join(objdir, image['imgname'])

		os.chdir(imgobjdir)
		# if computer == "martin":
		# 	os.system("sudo chown martin sig.fits")
		replaceNaN("sig.fits", 1.0e-8)
		replacezeroes("sig.fits", 1.0e-7)
		os.chdir(origdir)

	print "Done with NaN replacment."


	# And finally the cosmics :



	for i, image in enumerate(images):

		print "Cosmics %s %i/%i : %s" % (objkey, i+1, len(images), image["imgname"])

		imgobjdir = os.path.join(objdir, image['imgname'])
		os.chdir(imgobjdir)

		# We reset everyting :
		if os.path.isfile("cosmicsmask.fits"):
			os.remove("cosmicsmask.fits")
		if os.path.isfile("cosmicslist.pkl"):
			os.remove("cosmicslist.pkl")
		if os.path.isfile("orig_sig.fits"):
			# Then we reset the original sigma image :
			if os.path.isfile("sig.fits"):
				os.remove("sig.fits")
			os.rename("orig_sig.fits", "sig.fits")

		# We read array and header of that fits file :
		(a, h) = cosmics.fromfits("g.fits", verbose=False)

		# We gather some parameters :

		pssl = image['skylevel'] # The Previously Subtracted Sky Level
		print "PSSL (TM): %.2f" % pssl
		gain = image['gain']
		readnoise = image['readnoise']

		sigclip = cosmicssigclip
		sigfrac = 0.3
		objlim = 3.0

		# Creating the object :
		c = cosmics.cosmicsimage(a, pssl=pssl, gain=gain, readnoise=readnoise, sigclip=sigclip, sigfrac=sigfrac, objlim=objlim, satlevel=-1.0, verbose=False)
		# negative satlevel : we do not look for saturated stars


		# Ok let's try a full run :
		c.run(maxiter=3, verbose= False)

		ncosmics = np.sum(c.mask)

		# if ncosmics != 0:
		# 	print "--- %i pixels ---" % ncosmics

		# We do the rest anyway (easier):

		# We write the mask :
		cosmics.tofits("cosmicsmask.fits", c.getdilatedmask(size=5), verbose=False)

		# And the labels (for later png display) :
		cosmicslist = c.labelmask()
		writepickle(cosmicslist, "cosmicslist.pkl", verbose=False)

		# We modify the sigma image, but keep a copy of the original :
		os.rename("sig.fits", "orig_sig.fits")
		(sigarray, sigheader) = cosmics.fromfits("orig_sig.fits", verbose=False)
		sigarray[c.getdilatedmask(size=5)] = 1.0e-8 # again, it's inverted, hence the minus
		cosmics.tofits("sig.fits", sigarray, sigheader, verbose=False)

		os.chdir(origdir)


	notify(computer, withsound, "Done with extraction, NaN, and cosmics for %s." % objkey)
	
	



