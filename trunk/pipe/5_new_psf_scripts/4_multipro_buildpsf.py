#	
#	Does exactly the same as 4_buildpsf.py
#	
#	A first try to do this in parallel on several cores.
#	



execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil
from datetime import datetime, timedelta

import multiprocessing
import time



# Select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict', sortFields=['setname', 'mjd'])

# Remember where we are.
origdir = os.getcwd()


print "I will build the PSF of %i images." % len(images)

ncorestouse = multiprocessing.cpucount()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse
proquest(askquestions)


starttime = datetime.now()


# Now we have, as usual, a list of dicts to run on. Every PSF construction is perfectly independent, as we don't write common files or update the db etc.
# So this is a first try to run this in parallel on n processors.
# For this, we define a function, that takes an "image" (i.e. dictionnary from the list) as single argument.

for i, img in enumerate(images):
	img["execi"] = i # We do not write this into the db, it's just for this particular run.


def buildpsf(image):
	
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	
	print "Image %i : %s" % (image["execi"], imgpsfdir)
	
	# We go in the right dir (no confusions, i checked this)
	os.chdir(imgpsfdir)
	
	#time.sleep(1)
	#os.system("date > datetest.txt")
	#time.sleep(1)
	#print "Image %i : starting psf.exe ..." % image["execi"]
	#print "Testing %i" % image["execi"]
	#if not os.path.isfile("datetest.txt"):
	#	raise mterror("shit")
	#os.remove("datetest.txt")
		
	os.system(psfexe)
		
	# We go back home
	os.chdir(origdir)


# And we call the function, in a fork
pool = multiprocessing.Pool(processes=ncorestouse)
pool.map(buildpsf, images)
	

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

print "I'm done with the PSF construction for psfname: %s using %i cores." % (psfname, ncorestouse)
notify(computer, withsound, "Youpy. That's it. It took me %s ." % timetaken)
