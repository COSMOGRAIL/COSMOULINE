#
#	THIS IS FOR THE "OLD" DECONVOLUTION PROGRAMS !
#
#	obsds20, "psf.exe"
#	

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import shutil



origdir = os.getcwd()

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True, True, True], returnType='dict')
print "Number of images to treat :", len(images)
print "I will use the lambda file :"

f = open(old_lambda_template_filename, "r")
bla = f.readlines()
f.close()
print "".join(bla)

proquest(askquestions)

incompletedirs = []
	
for i, image in enumerate(images):
		
	print "- - - - - - - - - - - - - - - - - - - - - - - - "
	print i+1, image['imgname']
	#notify(computer, withsound, "Number %i, out of %i." %(i+1, len(images)))
	
	imgpsfdir = psfdir + image['imgname'] + "/"
	
	if not os.path.isfile(imgpsfdir + "mofc.fits"):
		print "no mofc.fits"
		incompletedirs.append(image['imgname'])
		continue # psfm.exe has not worked here so we skip it
		
	# lambda.txt : first line = inner, second line = outer, third = radius
	if os.path.isfile(imgpsfdir + "lambda.txt"):
		os.remove(imgpsfdir + "lambda.txt")
	
	if uselinks :
		os.symlink(old_lambda_template_filename , imgpsfdir + "lambda.txt")
	else: # copy the file
		shutil.copyfile(old_lambda_template_filename , imgpsfdir + "lambda.txt")
	
		
	
	
		# LET'S GO !!!
		
	if os.path.isfile(imgpsfdir + "s001.fits"):
		os.remove(imgpsfdir + "s001.fits")
	os.chdir(imgpsfdir)
	os.system(oldpsfexe)
	os.rename("s.fits", "s001.fits")
	os.chdir(origdir)
	
print "Done."

print "Incomplete psfmofs, skipped :"
for image in incompletedirs:
	print image
if len(incompletedirs) == 0:
	print "(None)"
if os.path.isfile(psfkicklist):
	print "The psfkicklist already exists :"
else:
	cmd = "touch " + psfkicklist
	os.system(cmd)
	print "I have just touched the psfkicklist for you :"

print psfkicklist
print "You should now append problematic psf constructions to that list."
