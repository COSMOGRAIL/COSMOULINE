#
#	NOW LOOK AT THIS !
#
#	Using pyfits, we will replace the zeroes in the sigma files prior to the psf construction
#	superfast, superclean...
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import astropy.io.fits as pyfits

	
origdir = os.getcwd()

	# select images to treat
db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme', objkeyflag], [True, True, True], returnType='dict')
print "Number of images to treat :", len(images)
proquest(askquestions)


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
	
	print i+1, "/", len(images), ":", image['imgname']
	imgobjdir = os.path.join(objdir, image['imgname'])
	
	os.chdir(imgobjdir)
	replaceNaN("sig.fits", 1.0e-8)
	replacezeroes("sig.fits", 1.0e-7)
	os.chdir(origdir)
	
notify(computer, withsound, "I replaced NaN for %s" % objkey)

	
