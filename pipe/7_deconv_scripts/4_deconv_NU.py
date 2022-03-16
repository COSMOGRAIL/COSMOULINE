#	
#	Do the deconvolution
#
import sys
import os

if len(sys.argv) == 2:
	exec (open("../config.py").read())
	decobjname = sys.argv[1]
	deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
	ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
	decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
	deckeyfilenum = "decfilenum_" + deckey
	deckeypsfused = "decpsf_" + deckey
	deckeynormused = "decnorm_" + deckey
	decdir = os.path.join(workdir, deckey)
	print("You are running the deconvolution on all the stars at once.")
	print("Current star : " + sys.argv[1])


else:
	exec (open("../config.py").read())

from kirbybase import KirbyBase, KBError
from variousfct import *
from datetime import datetime
from variousfct import *


if update:
	# override config settings...
	exec(open(os.path.join(configdir, 'deconv_config_update.py')).read())
	askquestions=False
	# nothing more. Let's run on the whole set of images now.

print("Starting deconvolution %s" % (deckey))

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum])
nbimg = len(images) + 1
print("%i images (ref image is duplicated)" % nbimg)

proquest(askquestions)

print("Of course I do not update the database here,")
print("so you can go on with something else in the meantime.")


starttime = datetime.now()
db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=[deckeyfilenum]) # WARNING the sorting is important !!!!!!!

origdir = os.getcwd()

os.chdir(decdir)
os.system(deconvexe)
os.chdir(origdir)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "I've deconvolved %s in %s ." % (deckey, timetaken))


