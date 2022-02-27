import shutil
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import configdir, settings, psfkey, psfstarcat, imgdb, dbbudir,\
                   psfdir, psfkeyflag, alidir
from modules.variousfct import proquest, backupfile, mterror
from modules import star
from modules.kirbybase import KirbyBase
from readandreplace_fct import justread, justreplace


askquestions = settings['askquestions']


db = KirbyBase()


print("psfkey =", psfkey)

print("Reading psf star catalog ...")
psfstars = star.readmancat(psfstarcat)
print("You want to use stars :")
for s in psfstars:
	print(s.name)


if settings['update']:
	askquestions = False

proquest(askquestions)

backupfile(imgdb, dbbudir, "prepare_" + psfkey)

# Then, we inpect the current siutation.
# Check if the psfdir already exists

if os.path.isdir(psfdir):
	print("This psfdir already exists. I will add or rebuild psfs in this set.")
	print("psfdir :", psfdir)
	proquest(askquestions)
	
	# Check if the psfkeyflag is in the database, to be sure it exists.
	if psfkeyflag not in db.getFieldNames(imgdb) :
		raise mterror("...but your corresponding psfkey is not in the database!")
	
	if settings['thisisatest']:
		print("This is a test !")
		print("So you want to combine/replace an existing psf with a test-run.")
		proquest(askquestions)
		
else :
	print("I will create a NEW psf.")
	print("psfdir :", psfdir)
	proquest(askquestions)
	if psfkeyflag not in db.getFieldNames(imgdb) :
		db.addFields(imgdb, ['%s:bool' % psfkeyflag])
	else:
		raise mterror("...funny: the psfkey was in the DB! Please clean psfdir and psfkey!")
	os.mkdir(psfdir)


# We select the images, according to "thisisatest".
# Note that only this first script of the psf construction looks at this :
# the next ones will simply  look for the psfkeyflag in the database !

if settings['thisisatest'] :
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], returnType='dict')
else :
	images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [True, True], returnType='dict')


print("I will treat %i images." % len(images))
proquest(askquestions)


# Read the config template
config_template = justread(os.path.join(configdir, "template_pyMCS_psf_config.py"))

# Format the psf stars catalog
nbrpsf = len(psfstars)
starscouplelist = repr([(int(s.x), int(s.y)) for s in psfstars])

for i,image in enumerate(images):

	print("- " * 40)
	print("%i / %i : %s" % (i+1, len(images), image['imgname']))
	
	# we clean the imgpsfdir :
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	if os.path.isdir(imgpsfdir):
		print("Deleting existing stuff.")
		shutil.rmtree(imgpsfdir)
	os.mkdir(imgpsfdir)
	
	
	os.mkdir(os.path.join(imgpsfdir, "images"))
	os.mkdir(os.path.join(imgpsfdir, "results"))
	
	# we put in the input image :
	if os.path.exists(os.path.join(imgpsfdir, "images", "in.fits")):
		os.remove(os.path.join(imgpsfdir, "images", "in.fits"))
	os.symlink(os.path.join(alidir, image['imgname'] + "_ali.fits") , \
               os.path.join(imgpsfdir, "images", "in.fits"))
	
	
	# we prepare the config :

	gain = "%f" % (image["gain"])
	stddev = "%f" % (image["stddev"])
	numpsfrad = "%f" % (6.0 * float(image["seeing"]))
	lambdanum = "%f" % (0.001) # image["seeing"]
	
	repdict = {'$gain$':gain, '$sigmasky$':stddev, \
              '$starscouplelist$':starscouplelist, '$numpsfrad$':numpsfrad,\
              '$lambdanum$' : lambdanum}	
	
	pyMCS_config = justreplace(config_template, repdict)
	extractfile = open(os.path.join(imgpsfdir, "pyMCS_psf_config.py"), "w")
	extractfile.write(pyMCS_config)
	extractfile.close()
	
	
	# and we update the database with a "True" for field psfkeyflag :
	db.update(imgdb, ['recno'], [image['recno']], [True], [psfkeyflag])
	


print("- " * 40)

db.pack(imgdb)
	
print("Done.")

