#
#	THIS IS FOR THE "OLD" DECONVOLUTION PROGRAMS !
#
#	we just want to build the psf, so I will erase g.fits, sig.fits etc to
#	avoid confusions.
#	
#	make the sub directories of psfdir in which the psf will be build for each image
#	write the input files for the extract.exe
#	do the extraction
#
#	Main work in this script is about selecting thr right images, preparing the database, 
#	and *adding* some treatme images to an existing psf, or creating a new one etc
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil

db = KirbyBase()

print "psfkey =", psfkey
proquest(askquestions)

# Let's see if the psfstarcat exists
print "Reading psf star catalog ..."
psfstars = readmancat(psfstarcat)
print "You want to use stars :"
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
		db.addFields(imgdb, ['%s:bool' % psfkeyflag])
	else:
		raise mterror("... funny : the psfkey was in the DB ! Please clean psfdir and psfkey !")
	os.mkdir(psfdir)


# We select the images, according to "thisisatest". Note that only this first script of the psf construction looks at this : the next ones will simply 
# look for the psfkeyflag in the database !

if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], [True, True, True], returnType='dict')
else :
	images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')


print "I will treat %i images." % len(images)
proquest(askquestions)

	# remember where we are.
origdir = os.getcwd()

	# format the psf stars catalog
nbrpsf = len(psfstars)
psfstarstxt = ""
for psfstar in psfstars:
	psfstarstxt = psfstarstxt + "%7.2f %7.2f\n" % (psfstar['x'], psfstar['y'])
psfstarstxt = psfstarstxt.rstrip("\n") # remove the last newline

	# read the template files
extract_template = justread(old_extract_template_filename)

n = 0
for image in images:

	print "- " * 40
	print n+1, "/", len(images), ":", image['imgname']
	n+=1
	imgpsfdir = psfdir + image['imgname'] + "/"
	
	if os.path.isdir(imgpsfdir):
		print "Deleting existing stuff."
		shutil.rmtree(imgpsfdir)
	os.mkdir(imgpsfdir)
	
	if uselinks :
		os.symlink(alidir + image['imgname'] + "_ali.fits" , imgpsfdir + "in.fits")
	else: # copy the image
		shutil.copyfile(alidir + image['imgname'] + "_ali.fits" , imgpsfdir + "in.fits")
	
	
	# we fill out our extract.txt
	
	extrdict = {"$imgname$": "in.fits", "$nbrpsf$": str(nbrpsf), "$gain$": str(image['gain']), "$stddev$": str(image['stddev']), "$psfstars$": psfstarstxt}
	#extrdict.update([["$psfstars$", psfstarstxt]])
	
	# not needed, I say "n" in the input file
	#lenscoord = "200.00 200.00"
	#extrdict.update([["$lenscoord$", lenscoord]])
	
	# tatatataaaa :
	extracttxt = justreplace(extract_template, extrdict)
	
	# and we write this into the file.
	extractfile = open(imgpsfdir + "extract.txt", "w")
	extractfile.write(extracttxt)
	extractfile.close()
	
	# we run the extraction
	os.chdir(imgpsfdir)
	os.system(oldextractexe)
	os.chdir(origdir)
	
	#os.remove(imgpsfdir + "g.fits")	# not needed anymore, as I said no in input for extract.exe
	#os.remove(imgpsfdir + "sig.fits")
	os.remove(imgpsfdir + "psfmof.txt") 	# incredibly useful file created by extract.exe ...
	os.remove(imgpsfdir + "param_psf.f") 	# even worse ...

	# and we update the database with a "True" for field psfkeyflag :
	db.update(imgdb, ['recno'], [image['recno']], [True], [psfkeyflag])

print "- " * 40
db.pack(imgdb)
	
print "This was the first script of the OLD psf construction."
print "I've prepared", n, "images."
	
	
