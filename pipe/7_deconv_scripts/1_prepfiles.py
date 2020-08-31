#	
#	Here we are. Finally.
#	The first main task of this script is to "put together" the right psfs for each image,
#	and complain if, for instance, one image has no psf, etc.
#	We have to look at the PSF rejection lists, as well as at the decskiplist.
#	We will do all this in memory, before touching to the database or starting anything.
#
#	Then :
#	copy the right stuff to the decdir, with the right filenames (0001, 0002, ...)
#	for identification, the "file-numbers" will be written into the db (as well as the psfname and norm coeff to use)
#
#	reference image will be put at first place, i.e. 0001
#
#	
import sys
if len(sys.argv) == 2:
	execfile("../config.py")
	decobjname = sys.argv[1]
	deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
	ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
	decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
	deckeyfilenum = "decfilenum_" + deckey
	deckeypsfused = "decpsf_" + deckey
	deckeynormused = "decnorm_" + deckey
	decdir = os.path.join(workdir, deckey)
	print "You are running the deconvolution on all the stars at once."
	print "Current star : " + sys.argv[1]

else :
	execfile("../config.py")

from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *



if update:
	# override config settings...
	execfile(os.path.join(configdir, 'deconv_config_update.py'))
	askquestions=False
	# nothing more. Let's run on the whole set of images now.

# Some first output for the user to check :
print "Name for this deconvolution : %s." % decname
if thisisatest :
	print "This is a test run."
else :
	print "This is NOT a test run !"
print "You want to deconvolve the object '%s' with the PSFs from :" % decobjname
for psfname in decpsfnames:
	print psfname
print "And you want to normalize using :", decnormfieldname

proquest(askquestions)

# And a check of the status of the decskiplist :

if os.path.isfile(decskiplist):
	print "The decskiplist already exists :"
else:
	cmd = "touch " + decskiplist
	os.system(cmd)
	print "I have just touched the decskiplist for you :"
print decskiplist

decskipimages = [image[0] for image in readimagelist(decskiplist)] # image[1] would be the comment
print "It contains %i images." % len(decskipimages)

#proquest(askquestions)


# We have a look at the psfkicklists and the flags for each psf in the database:

print "Ok, now looking at the PSFs ..."

psfimages = {}	# we will build a dictionary, one entry for each psfname, containing
		# available images.

db = KirbyBase()		
for particularpsfname in decpsfnames:
	print "- " * 30
	# the database
	particularpsfkey = "psf_" + particularpsfname
	particularpsfkeyflag = "flag_" + particularpsfkey
	particulartreatedimages = [image[0] for image in db.select(imgdb, [particularpsfkeyflag], [True], ['imgname'])] # we get a list of imgnames
	# the [0] is just to get rid of the list-of-list structure
	
	# the skiplist
	particularskiplist = os.path.join(configdir, particularpsfkey + "_skiplist.txt")
	particularskiplistimages = [image[0] for image in readimagelist(particularskiplist)] # image[1] would be the comment
	
	print "%15s : %4i images, but %3i on skiplist" % (particularpsfname, len(particulartreatedimages), len(particularskiplistimages))
	
	# ok, now we combine the two lists :
	
	particulartreatedimages = set(particulartreatedimages)
	particularskiplistimages = set(particularskiplistimages)
	if not particularskiplistimages.issubset(particulartreatedimages):
		errors = particularskiplistimages.difference(particulartreatedimages)
		print "WARNING : the following skiplist items are not part of that PSF set !"
		print "They might be typos ..."
		for error in errors:
			print error
	particularavailableimages = particulartreatedimages.difference(particularskiplistimages)
	print "Number of available psfs :", len(particularavailableimages)
	
	psfimages[particularpsfname] = list(particularavailableimages) # here we add those to the dict.

print "- " * 30
#proquest(askquestions)
		
# Now we should be able to attribute one precise psf for every image to deconvolve.
# we start by selecting the images we want to use (treatme and or testlist, as usual)
# before this you could perhaps put treatme (or gogogo ?) to false for bad seeing etc...

if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	refimage = [image for image in images if image['imgname'] == refimgname][0]
else :
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])
	refimage = [image for image in images if image['imgname'] == refimgname][0]


print "Number of images selected from database (before psf attribution or decskiplist) :", len(images)
#proquest(askquestions)


# images is now a list of dicts. We will write the psf to use into this dict.

for image in images:
	image['choosenpsf'] = "No psf"
	for psfname in decpsfnames:
		if image['imgname'] in psfimages[psfname]:
			image['choosenpsf'] = psfname
	# this means that the last psf available from the decpsfnames will be used.


nopsfimages = [image['imgname'] for image in images if image['choosenpsf'] == "No psf"]
if len(nopsfimages) > 0:
	print "WARNING : I found %i images without available psf :" % len(nopsfimages)
	for imagename in nopsfimages:
		print imagename
	print "I will thus not use them in the deconvolution !"

havepsfimages = [image for image in images if image['choosenpsf'] != "No psf"]
print "Number of images that have a valid PSF (again, before looking at decskiplist) :", len(havepsfimages)
#proquest(askquestions)

# we do now a check for the object extraction
# Missing objects are not tolerated. We would simply stop.

print "Now looking for the object itself ..."

objkey = "obj_" + decobjname
objkeyflag = "flag_" + objkey

if objkeyflag not in db.getFieldNames(imgdb):
	raise mterror("Your object %s is not yet extracted !"%decobjname)
noobjimages = [image['imgname'] for image in images if image[objkeyflag] != True]
if len(noobjimages) > 0:
	raise mterror("%i images have no objects extracted !"%len(noobjimages))

objimages = [image['imgname'] for image in images if image[objkeyflag] == True] 
print "I've found", len(objimages), "extracted objects."	# In fact this is trivial, will not be used later.

#proquest(askquestions)
# havepsfimages are for now the ones to go.
# It's time to look at the decskipimages.

print "Images that have a valid PSF :", len(havepsfimages)
print "Images on your decskiplist :", len(decskipimages)	# note that this list contains only the names !
readyimages = [image for image in havepsfimages if image["imgname"] not in decskipimages]
print "Images with valid PSF not on decskiplist :", len(readyimages)
print "(i.e. I will prepare the deconvolution for this last category !)"

if len(readyimages) >= 2500:
	print "This is too much, MCS in fortran can only handle less than 2500 images."
	sys.exit()

# We don't do this check anymore. It can well be that images on the decskiplist have been already demoted for other reasons.
#if len(readyimages) != len(havepsfimages) - len(decskipimages):
#	print "THIS IS FISHY... but ok, I don't mind."

# But while we are at it let's check if there are any "typos" in the decskiplist :
possibleimagenameset = set([imgnamelist[0] for imgnamelist in db.select(imgdb, ['recno'], ['*'], ["imgname"])])
decskipimagenameset = set(decskipimages)

if not decskipimagenameset.issubset(possibleimagenameset):
	errors = decskipimagenameset.difference(possibleimagenameset)
	print "WARNING : I can't find the following decskiplist items in the database !"
	for error in errors:
		print error
	raise mterror("Fix this (see above output).")

#proquest(askquestions)


# a check about the reference image:
if refimgname not in [image['imgname'] for image in readyimages] :
	print "The reference image is not in your initial selection ! \n Do you want me to add it ? Or do you prefer for me to crash ?"
	proquest(askquestions)
	readyimages.append(refimage)
if refimgname in nopsfimages :
	raise mterror("No PSF available for reference image !")


# we check if this deconvolution was already done before :

if os.path.isdir(decdir):	# start from empty directory
	print "I will delete the existing deconvolution."
	proquest(askquestions)
	shutil.rmtree(decdir)
	print "It's too late to cry now."
	os.mkdir(decdir)
else :
	os.mkdir(decdir)

# everything seems fine for the input so let's go

print "I will now prepare the database. deckey :", deckey # this is a code that will idendtify this particular deconvolution.
proquest(askquestions)
backupfile(imgdb, dbbudir, "prepfordec_"+deckey)


if deckeyfilenum in db.getFieldNames(imgdb):
	db.dropFields(imgdb, [deckeyfilenum, deckeypsfused, deckeynormused])	# we erase the previous fields for this deckey
						# this full erase is important, as we will use the simple
						# presence of these numbers to identify 
						# images used in this deconvolution !
db.addFields(imgdb, ['%s:str' % deckeyfilenum, '%s:str' % deckeypsfused, '%s:float' % deckeynormused])
	


# Now we have to "copy" the reference image to the first position.
# But we will leave it inside the normal list, so it will be duplicated.



# We select the reference image
refimage = [image for image in readyimages if image['imgname'] == refimgname][0] # we take the first and only element.
# And copy it into the first positon :
readyimages.insert(0, refimage)
# readyimages now contains n+1 images !!!!

for i, image in enumerate(readyimages):

	decfilenum = mcsname(i+1); # so we start at i = 1 !!! i = 1 is reserved for the copy of the ref image.
	print "- " * 40
	print decfilenum, "/", len(readyimages), ":", image['imgname']
	
	# We know which psf to use :
	print "PSF : %s" % image['choosenpsf']
	
	# We select the normalization on the fly, as this is trivial compared to the psf selection :
	if decnormfieldname == "None":
		image["choosennormcoeff"] = 1.0	# in this case the user *wants* to make a deconvolution without normalization.
	else :
		image["choosennormcoeff"] = image[decnormfieldname]
		if image["choosennormcoeff"] == None:
			print "WAAAAAAAAARRRRRNIIIIING : no coeff available, using 1.0 !"
			image["choosennormcoeff"] = 1.0
	print "Norm. coefficient : %.3f" % image["choosennormcoeff"]
		
		
	psfdir = os.path.join(workdir, "psf_" + image['choosenpsf'])
	objdir = os.path.join(workdir, "obj_" + decobjname)	# this should not have changed
	imgpsfdir = os.path.join(psfdir, image['imgname'])	# we take the psf from here
	imgobjdir = os.path.join(objdir, image['imgname'])	# and the g.fits + sig.fits here

	os.symlink(os.path.join(imgpsfdir +"/results","s_1.fits") , os.path.join(decdir, "s%s.fits" % decfilenum)) #fix here : go back to the original file instead of the alias that might be corrupted
	os.symlink(os.path.join(imgobjdir, "g.fits") , os.path.join(decdir, "g%s_notnorm.fits" % decfilenum))
	os.symlink(os.path.join(imgobjdir, "sig.fits") , os.path.join(decdir, "sig%s_notnorm.fits" % decfilenum))


	# For the duplicated ref image, we do not update the database !
	# As in fact, there is no duplicated ref image in the database...
	if i != 0 : # that is mcsname != 0001
		db.update(imgdb, ['recno'], [image['recno']], {deckeyfilenum: decfilenum, deckeypsfused: image['choosenpsf'], deckeynormused: image["choosennormcoeff"]})

	# numbers in the db start with 0002

print "- " * 40
db.pack(imgdb)
notify(computer, withsound, "Hello again.\nI've prepared %i images for %s"%(len(readyimages), deckey))
print "(Yes, one more, as I duplicated the ref image.)"
