#
#	THIS IS FOR THE "OLD" DECONVOLUTION PROGRAMS !
#
#	we write the input file for the old psfm.exe and do it
#
#	To distribute this on multiple processors, I like to use an alternative image selection according to setname...
#	

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil
from datetime import datetime, timedelta

origdir = os.getcwd()

	# select images to treat
db = KirbyBase()

images = db.select(imgdb, ['gogogo', 'treatme', psfkeyflag], [True, True, True], returnType='dict')
# you can tweak this like below to separate for multiple processors.
#images = db.select(imgdb, ['setname', psfkeyflag], ['MaiSITE1', True], returnType='dict')



print "Number of images to treat :", len(images)
proquest(askquestions)


	# read and format the psf stars catalog
psfstars = readmancat(psfstarcat)
nbrpsf = len(psfstars)

	# read the template files
psf_template = justread(old_psfm_template_filename)

starttime = datetime.now()

for i, image in enumerate(images):
	
	print "- - - - - - - - - - - - - - - - - - - - - - - - "
	print i+1, "/", len(images), ":", image['imgname']
	notify(computer, withsound, "Number %i, out of %i." %(i+1, len(images)))
	
	
	imgpsfdir = psfdir + image['imgname'] + "/"
	
	# psfmof.txt
	
	resolpix = 0.9 * image["seeingpixels"]
	# there is no true reason for this 0.9 but it seems to bug less
	
	print "seeingpixels :", image["seeingpixels"]
	print "resolpix :", resolpix
	
		# preparation of the last lines of the input file
	parampsf = ""
	for i, psfstar in enumerate(psfstars):
		
		parampsf = parampsf + " %3.1f\t%4.1f\t%4.1f\n" % (1.0, 66.0, 66.0)
		
	parampsf = parampsf.rstrip("\n") # remove the last newline
	
	psfdict = {"$nbrpsf$": str(nbrpsf), "$resolpix$": str(resolpix), "$parampsf$": parampsf}
	
	psfmoftxt = justreplace(psf_template, psfdict)
	psfmoffile = open(imgpsfdir + "psfmof.txt", "w")
	psfmoffile.write(psfmoftxt)
	psfmoffile.close()
	
	
		# LET'S GO !!!
	os.chdir(imgpsfdir)
	os.system(oldpsfmexe)
	os.chdir(origdir)

endtime = datetime.now()

timetaken = nicetimediff(endtime - starttime)

notify(computer, withsound, "Dave ? \nDo you hear me Dave ?\nI have successfully fitted %i Moffat functions. I would like to apologize : this took me %s. ." % (len(images), timetaken))
	
	
