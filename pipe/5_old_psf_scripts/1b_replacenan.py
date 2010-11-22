#
#	THIS IS FOR THE "OLD" DECONVOLUTION PROGRAMS !
#
#	Using pyfits, we will replace the zeroes in the sigma files prior to the psf construction
#	superfast, superclean...
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import pyfits


origdir = os.getcwd()

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme',psfkeyflag], [True,True,True], returnType='dict')
print "Number of images to treat :", len(images)
proquest(askquestions)

psfstars = readmancat(psfstarcat)
nbrpsf = len(psfstars)


def isNaN(x):
	return x!=x
	
def replaceNaN(filename, value):
	sigstars = pyfits.open(filename, mode='update')
	scidata = sigstars[0].data
	if True in isNaN(scidata):
		print "Yep, some work for me : ", len(scidata[isNaN(scidata)]), "pixels."
	scidata[isNaN(scidata)] = value
	sigstars.flush()

def replacezeroes(filename, value):
	myfile = pyfits.open(filename, mode='update')
	scidata = myfile[0].data
	for x in range(len(scidata)):
		for y in range(len(scidata[0])):
			if scidata[x][y] < 1.0e-8:
				print "Nearly zero at ", x, y
				scidata[x][y] = value
	myfile.flush()
	
	
for i, image in enumerate(images):
	
	print i+1, image['imgname']
	imgpsfdir = os.path.join(psfdir, image['imgname'])
	
	os.chdir(imgpsfdir)
	
	for i in range(nbrpsf):
		j = i+1
		sigfilename = "psfsig%02d.fits"%j
		psffilename = "psf%02d.fits"%j
		print sigfilename
		replaceNaN(sigfilename, 1.0e8)
		#replacezeroes(sigfilename, 1.0e-6)
		
		#replaceNaN(psffilename, 1.0e6)
		#replacezeroes(psffilename, 1.0e-6)
		# exactly : for the old psf programs, we need big values here !

	os.chdir(origdir)
	
print "Done."
	
	
