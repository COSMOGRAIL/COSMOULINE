execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime, timedelta
import forkmap
#import multiprocessing  # if forkmap fails...
import star
from readandreplace_fct import *

import src.lib.utils as fn
from MCS_interface import MCS_interface

####
rewriteconfig = True
nofitnum = False
redofromscratch = True
####

if rewriteconfig == True:
	psfstars = star.readmancat(psfstarcat)
	nbrpsf = len(psfstars)
	starscouplelist = repr([(int(s.x), int(s.y)) for s in psfstars])
	config_template = justread(os.path.join(configdir, "template_pyMCS_psf_config.py"))

# Select images to treat
db = KirbyBase()

if thisisatest :
	print "This is a test run."
	images = db.select(imgdb, ['gogogo', 'treatme', 'testlist',psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
elif update:
	print "This is an update."
	images = db.select(imgdb, ['gogogo', 'treatme', 'updating', psfkeyflag], [True, True, True, True], returnType='dict', sortFields=['setname', 'mjd'])
	askquestions=False
else :
	images = db.select(imgdb, ['gogogo', 'treatme',psfkeyflag], [True, True, True], returnType='dict', sortFields=['setname', 'mjd'])

print "I will build the PSF of %i images." % len(images)

ncorestouse = forkmap.nprocessors()
#ncorestouse = multiprocessing.cpu_count()

if computer == "martin": #patch to fix the the forkmap bug (crash under macOSX)
	maxcores = 1

if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)


psfstars = star.readmancat(psfstarcat)  # this is only used if nofitnum
print "We have %i stars" % (len(psfstars))
#for star in psfstars:
#	print star.name

errorimglist = []

for i, img in enumerate(images):
	img["execi"] = (i+1) # We do not write this into the db, it's just for this particular run.

def buildpsf(image):

	imgpsfdir = os.path.join(psfdir, image['imgname'])
	if os.path.isfile(os.path.join(imgpsfdir, "results", "psf_1.fits")) and not redofromscratch:
		print "Image %i : %s" % (image["execi"], imgpsfdir)
		print "Already done ! I skip this one"
		return
	else:


		print "Image %i : %s" % (image["execi"], imgpsfdir)

		os.chdir(imgpsfdir)

		if rewriteconfig == True:
		# We redo the copy of the config, in case something was changed in the template for testing different parameters:

			gain = "%f" % (image["gain"])
			stddev = "%f" % (image["stddev"])
			numpsfrad = "%f" % (6.0 * float(image["seeing"]))
			lambdanum = "%f" % (0.001) # image["seeing"]

			repdict = {'$gain$':gain, '$sigmasky$':stddev, '$starscouplelist$':starscouplelist, '$numpsfrad$':numpsfrad, '$lambdanum$' : lambdanum}

			pyMCS_config = justreplace(config_template, repdict)
			extractfile = open(os.path.join(imgpsfdir, "pyMCS_psf_config.py"), "w")
			extractfile.write(pyMCS_config)
			extractfile.close()

			print "I rewrote the config file."

		mcs = MCS_interface("pyMCS_psf_config.py")

		try:
			print "I'll try this one."
			mcs.fitmof()
			if nofitnum:
				mcs.psf_gen()
				# Then we need to write some additional files, to avoid png crash
				empty128 = np.zeros((128, 128))
				tofits("results/psfnum.fits", empty128)
				empty64 = np.zeros((64, 64))
				for i in range(len(psfstars)):
					tofits("results/difnum%02i.fits" % (i+1), empty64)

			else:
				mcs.fitnum()

		except (IndexError):
			print "WTF, an IndexError ! "
			errorimglist.append(image)

		else:
			print "It worked !"

		psffilepath = os.path.join(imgpsfdir, "s001.fits")
		if os.path.islink(psffilepath):
			os.remove(psffilepath)
		os.symlink(os.path.join(imgpsfdir, "results", "s_1.fits"), psffilepath)
	
	
starttime = datetime.now()
#pool = multiprocessing.Pool(processes=ncorestouse)
#pool.map(buildpsf, images)
forkmap.map(buildpsf, images, n = ncorestouse)
endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

if os.path.isfile(psfkicklist):
	print "The psfkicklist already exists :"
else:
	cmd = "touch " + psfkicklist
	os.system(cmd)
	print "I have just touched the psfkicklist for you :"
print psfkicklist

if len(errorimglist) != 0:
	print "pyMCS raised an IndexError on the following images :"
	print "(Add them to the psfkicklist, retry them with a testlist, ...)"
	print "\n".join(["%s\t%s" % (image['imgname'], "pyMCS IndexError") for image in errorimglist])
else:
	print "I could build the PSF of all images."

notify(computer, withsound, "PSF construction for psfname: %s using %i cores. It took me %s ." % (psfname, ncorestouse, timetaken))

