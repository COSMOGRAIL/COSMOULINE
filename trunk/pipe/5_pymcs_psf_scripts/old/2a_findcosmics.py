#
#	THIS IS FOR THE "OLD" DECONVOLUTION PROGRAMS !
#
#	We use cosmics.py to locate cosmics in the psfnn.fits images.
#	We do not clean them, but mask them in the psfsignn.fits.
#	The database is updated with the number of cosmic rays found.
#
#	It is ok to relauch this script : 
#		- I will reset the database entry
#		- Erase any previous files
#		- Apply my mask on the original sigma image.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import cosmics

	# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict')
print "Number of images to treat :", len(images)
proquest(askquestions)

	# Find how many PSF stars we have
psfstars = readmancat(psfstarcat)
nbrpsf = len(psfstars)

	# Remember where we are
origdir = os.getcwd()

	# The database needs update :
print "I will update the database and start, key = %s" % cosmicskey
proquest(askquestions)
backupfile(imgdb, dbbudir, "find_" + cosmicskey)

if cosmicskey not in db.getFieldNames(imgdb) :
	db.addFields(imgdb, ['%s:int' % cosmicskey])
else:
	print "Ok, the field %s already exists in the database." % cosmicskey

	# Go !
for i, image in enumerate(images):
	
	print "%i : %s" % (i+1, image['imgname'])
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	os.chdir(imgpsfdir)
	
	totcosmics = 0
	
	for i in range(1, nbrpsf+1):
		psffilename = "psf%02d.fits" % i
		sigfilename = "psfsig%02d.fits" % i
		
		print psffilename
		
		# We reset everyting :
		if os.path.isfile("cosmicsmask%02d.fits" % i):
			os.remove("cosmicsmask%02d.fits" % i)
		if os.path.isfile("cosmicslist%02d.pkl" % i):
			os.remove("cosmicslist%02d.pkl" % i)
		if os.path.isfile("orig_psfsig%02d.fits" % i):
			# Then we reset the original sigma image :
			if os.path.isfile("psfsig%02d.fits" % i):
				os.remove("psfsig%02d.fits" % i)
			os.rename("orig_psfsig%02d.fits" % i, "psfsig%02d.fits" % i)
		
		# We read array and header of that fits file :
		(a, h) = cosmics.fromfits(psffilename, verbose=False)
		
		# This %&*#! is normalized by shitty extract.exe
		# So we keep calm and check the sextractor catalog...
		# No way...
		
		a = a * 1000.0 # minimal peak value of a good PSF star ...
		# Brighter stars will be smoother, so less chance to detect cosmics.
		
		# We gather some parameters :
		
		pssl = image['skylevel'] # The Previously Subtracted Sky Level
		gain = image['gain']
		readnoise = image['readnoise']
		# Now we have a noisemap around sqrt(image)
		
		sigclip = 4.0
		sigfrac = 0.2
		objlim = 3.0
		
		# Creating the object :
		c = cosmics.cosmicsimage(a, pssl=pssl, gain=gain, readnoise=readnoise, sigclip=sigclip, sigfrac=sigfrac, objlim=objlim, verbose=False)
		
		# We do not need the full artillery, one L.A.Cosmic iteration
		# should do it.
		ladict = c.lacosmiciteration()
		
		ncosmics = ladict["niter"]
		totcosmics = totcosmics + ncosmics
		
		if ncosmics != 0:
			print "--- %i pixels ---" % ncosmics
			
		# We write the mask :
		cosmics.tofits("cosmicsmask%02d.fits" % i, c.getdilatedmask(size=5), verbose=False)
			
		# And the labels (for later png display) :
		cosmicsdict = c.labelmask()
		writepickle(cosmicsdict, "cosmicslist%02d.pkl" % i, verbose=False)
		
		# We modify the sigma image, but keep a copy of the original :
		os.rename("psfsig%02d.fits" % i, "orig_psfsig%02d.fits" % i)
		(sigarray, sigheader) = cosmics.fromfits("orig_psfsig%02d.fits" % i, verbose=False)
		sigarray[c.getdilatedmask(size=5)] = 1.0e8 # yes, for the old psf
		cosmics.tofits("psfsig%02d.fits" % i, sigarray, sigheader, verbose=False)
			
	# We write the total number of cosmics in the database :
	db.update(imgdb, ['recno'], [image['recno']], {cosmicskey: int(totcosmics)})
	os.chdir(origdir)

db.pack(imgdb) # To erase the blank lines
print "Done."
	
	
