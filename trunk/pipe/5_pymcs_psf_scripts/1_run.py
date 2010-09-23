
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *


db = KirbyBase()

print "Hehe."

print "psfkey =", psfkey
proquest(askquestions)

# Let's see if the psfstarcat exists
print "Reading psf star catalog ..."
psfstars = readmancat(psfstarcat)
print "You want to use stars :"
for star in psfstars:
	print star['name']
proquest(askquestions)

backupfile(imgdb, dbbudir, "prepare_" + psfkey)

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

	# Copy the pyMCS directory to where we need it ...

pymcsworkdir = os.path.join(psfdir, "pyMCS")
if os.path.isdir(pymcsworkdir): # We remove any previous copy of pyMCS
	shutil.rmtree(pymcsworkdir)
if not os.path.isdir(pymcsdir):
	raise mterror("Cannot find pyMCS !")
shutil.copytree(pymcsdir, pymcsworkdir)

	# Read the config templage

config_template = justread(pyMCS_config_template_filename)

	# format the psf stars catalog
nbrpsf = len(psfstars)
starlist = repr([(int(star['x']), int(star['y'])) for star in psfstars])

for i,image in enumerate(images):

	print "- " * 40
	print "%i / %i : %s" % (i+1, len(images), image['imgname'])
	
	# we clean the imgpsfdir :
	imgpsfdir = psfdir + image['imgname'] + "/"
	if os.path.isdir(imgpsfdir):
		print "Deleting existing stuff."
		shutil.rmtree(imgpsfdir)
	os.mkdir(imgpsfdir)
	
	# and the pymcsworkdir :
	if os.path.isdir(os.path.join(pymcsworkdir, "results")):
		shutil.rmtree(os.path.join(pymcsworkdir, "results"))
		os.mkdir(os.path.join(pymcsworkdir, "results"))
	if os.path.isdir(os.path.join(pymcsworkdir, "results")):
		shutil.rmtree(os.path.join(pymcsworkdir, "results"))
		os.mkdir(os.path.join(pymcsworkdir, "results"))
	
	# we put in the input image :
	if os.path.isfile(os.path.join(pymcsworkdir, "img", "in.fits")):
		os.remove(os.path.join(pymcsworkdir, "img", "in.fits"))
	os.symlink(alidir + image['imgname'] + "_ali.fits" , os.path.join(pymcsworkdir, "img", "in.fits"))
	
	os.symlink(alidir + image['imgname'] + "_ali.fits" , os.path.join(imgpsfdir, "in.fits"))
	
	# we prepare the config :
	gain = "%f" % image["gain"]
	stddev = "%f" % image["stddev"]
	repdict = {'$gain$':gain, '$stddev$':stddev, '$starlist$':starlist}	
	
	pyMCS_config = justreplace(config_template, repdict)
	extractfile = open(os.path.join(pymcsworkdir, "config.py"), "w")
	extractfile.write(pyMCS_config)
	extractfile.close()
	
	# and now ...
	os.chdir(pymcsworkdir)
	os.system("python _3_fitmof.py")
	os.system("python _4_fitgaus.py")
	os.chdir(origdir)
	
	# we move all this stuff into the imgpsfdir :
	if os.path.isdir( os.path.join(imgpsfdir, "results")):
		shutil.rmtree(os.path.join(imgpsfdir, "results"))
	shutil.copytree(os.path.join(pymcsworkdir, "results"), os.path.join(imgpsfdir, "results"))
	
	shutil.copy(os.path.join(pymcsworkdir, "config.py"), os.path.join(imgpsfdir, "config.py"))
	
	
	# and we update the database with a "True" for field psfkeyflag :
	db.update(imgdb, ['recno'], [image['recno']], [True], [psfkeyflag])


print "- " * 40

db.pack(imgdb)
	
print "Done."
