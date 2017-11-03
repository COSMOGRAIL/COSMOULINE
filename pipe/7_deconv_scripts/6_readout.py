#
#	Read the produced out.txt
#	And write it into the database, using nice custom field names (using deckey and the source names)
#	*proud*
#	Final victory over this lovely deconv.exe output file ...
#
# For each source we insert x, y, flux = the acutal flux, calculated with a bizarre formula from the MCS intensity.
# Plus there is z1, z2, delta1, delta2 and the photonic shot noise.
#
#	WARNING  : the flux is "denormalized" by whatever normalization coeff you had used.
#	So we write raw fluxes into the db, not normalized ones !
#

import sys
if len(sys.argv) == 2:
	execfile("../config.py")
	decobjname = sys.argv[1]
	deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
	ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
	decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
	deckeyfilenum = "decfilenum_" + deckey
	deckeypsfused = "decpsf_" + deckey
	deckeynormused = "decnorm_" + deckey
	decdir = os.path.join(workdir, deckey)
	print "You are running the readout on all the stars at once."
	print "Current star : " + sys.argv[1]

else :
	execfile("../config.py")
	
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import star
import progressbar
import numpy as np
import variousfct
import scipy

if update:
	# override config settings...
	execfile(os.path.join(configdir, 'deconv_config_update.py'))
	askquestions=False
	# nothing more. Let's run on the whole set of images now.


def rebin(a, newshape):
	"""
	Auxiliary function to rebin ndarray data. -> we put the *mean* of the orig pixels into the new ones.
	Source : http://www.scipy.org/Cookbook/Rebinning
        example usage:
        >>> a=rand(6,4); b=rebin(a,(3,2))
        """
        shape = a.shape
        lenShape = len(shape)
        factor = np.asarray(shape)/np.asarray(newshape)

        evList = ['a.reshape('] + \
                 ['newshape[%d],factor[%d],'%(i,i) for i in xrange(lenShape)] + \
                 [')'] + ['.sum(%d)'%(i+1) for i in xrange(lenShape)] + \
                 ['/factor[%d]'%i for i in xrange(lenShape)]

        return eval(''.join(evList))


db = KirbyBase()
# We select only the images that are deconvolved (and thus have a deckeyfilenum)
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True) # the sorting is not  important

# We duplicate the ref image, this will be easier for the output reading.
refimage = [image for image in images if image['imgname'] == refimgname][0] # we take the first and only element.
images.insert(0, refimage.copy()) # This copy is important !!!
images[0][deckeyfilenum] = mcsname(1) # The duplicated ref image gets number 1

nbimg = len(images)
print "Number of images (including duplicated reference) : %i" % (nbimg)




	# read params of point sources
ptsrcs = star.readmancat(ptsrccat)
nbptsrcs = len(ptsrcs)
print "Number of point sources :", nbptsrcs
print "Names of sources : "
for src in ptsrcs: print src.name

# The readout itself is fast :
intpostable, zdeltatable = readouttxt(os.path.join(decdir, "out.txt"), nbimg)
# We give nbimg, so the readouttxt fct does not know that the first image is a duplication of the ref.

print "Ok, I've read the deconvolution output.\n"




# We now prepare a list of dictionnaries to be written into the database, as well as a list of fields to add to the db.

newfields = []
for src in ptsrcs:

	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_flux", "type": "float"}) # This will contain the flux (as would be measured by aperture  photometry on the original raw image)
	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_x", "type": "float"})
	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_y", "type": "float"})
	newfields.append({"fieldname": "out_" + deckey + "_" + src.name + "_shotnoise", "type": "float"}) # this will contain the shot noise of the flux (including sky level, psf shape)
newfields.append({"fieldname": "out_" + deckey + "_z1", "type":"float"})
newfields.append({"fieldname": "out_" + deckey + "_z2", "type":"float"})
newfields.append({"fieldname": "out_" + deckey + "_delta1", "type":"float"})
newfields.append({"fieldname": "out_" + deckey + "_delta2", "type":"float"})


#print "Negative fluxes :"
negfluxes = []

for image in images:

	print "%s : %s" % (image[deckeyfilenum], image["imgname"])
	
	image["updatedict"] = {}
	outputindex = int(image[deckeyfilenum]) - 1 # So this guy is starting at 0, even if the first image is 0001.
	
	image["updatedict"]["out_" + deckey + "_z1"] = zdeltatable[outputindex][0]
	image["updatedict"]["out_" + deckey + "_z2"] = zdeltatable[outputindex][1]
	image["updatedict"]["out_" + deckey + "_delta1"] = zdeltatable[outputindex][2]
	image["updatedict"]["out_" + deckey + "_delta2"] = zdeltatable[outputindex][3]
	
	
	# Reading the PSF, to calculate shotnoise:
	psffilepath = os.path.join(decdir, "s%s.fits" % image[deckeyfilenum])
	(mcspsf, h) = variousfct.fromfits(psffilepath, verbose=False)

	# We rearrange the PSF quadrants so to have it in the center of the image.
	ramcspsf = np.zeros((128, 128))
	ramcspsf[0:64, 0:64] = mcspsf[64:128, 64:128]
	ramcspsf[64:128, 64:128] = mcspsf[0:64, 0:64]
	ramcspsf[64:128, 0:64] = mcspsf[0:64, 64:128]
	ramcspsf[0:64, 64:128] = mcspsf[64:128, 0:64]
	
	#print "Sum of mcsPSF : %.6f" % np.sum(ramcspsf)
	# We convolve it with a gaussian of width = 2.0 "small pixels".
	smallpixpsf = scipy.ndimage.filters.gaussian_filter(ramcspsf, 2.0)
	#print "Sum of PSF : %.6f" % np.sum(smallpixpsf)
	# We rebin it, 2x2 :
	psf = 4.0*rebin(smallpixpsf, (64, 64))
	#print "Sum of rebinned PSF : %.6f" % np.sum(psf)
	# We calculate the sharpness :
	sharpness = np.sum(psf * psf)
	print "Equivalent pixels : %.2f" % float(1.0/sharpness)
	
	# For info about this, see :
	# Heyer, Biretta, et al. 2004, WFPC2 Instrument Handbook, Version 9.0m (Baltimore: STScI), Chapter 6
	# http://www.stsci.edu/hst/observatory/etcs/etc_user_guide/1_3_optimal_snr.html

	
	for i, src in enumerate(ptsrcs):

		# image["updatedict"]["out_" + deckey + "_" + src.name + "_int"] = intpostable[i][outputindex][0]
		image["updatedict"]["out_" + deckey + "_" + src.name + "_x"] = intpostable[i][outputindex][1]
		image["updatedict"]["out_" + deckey + "_" + src.name + "_y"] = intpostable[i][outputindex][2]
		
		# We calculate the flux :
		
		fwhm = 2.0 # this is the width of the "output gaussian", that we choose to be of 2 small pixels
		pi = 3.141592653589793
		ln2 = 0.693147180559945
		
		mcsint = intpostable[i][outputindex][0] # the mcs intensity
		flux = mcsint * ( fwhm**2 / 4.0 ) * pi / (4.0 * ln2)
		
		
		# We check if the flux is positive :
		if flux < 0.0:
			negfluxes.append("%s\t%s, %s : flux = %f " % (image["imgname"], image["datet"], src.name, flux))

		# the shot noise
		
		# version 1.0 : gives to large errorbars. We are not doing aperture photometry here, but psf fitting.
		#skyflux = 64.0*64.0*image["skylevel"]	# this is the flux of the sky in a box of the size of the frame used to deconvole objects
		#shotnoise = np.sqrt(skyflux + flux)	# this is the shot noise of the not normalized flux (skyflux is anyway not normalized)
		
		shotnoise = float(np.sqrt(flux + ((image["skylevel"] + image["readnoise"]**2.0)/sharpness)))
	
		print "\t%s : \t%9.2f +/- %5.2f %%" % (src.name, flux, 100*shotnoise/flux)

		# We *** denormalize *** :
		flux = flux / image[deckeynormused]
		shotnoise = shotnoise / image[deckeynormused]
		
		image["updatedict"]["out_" + deckey + "_" + src.name + "_flux"] = flux
		image["updatedict"]["out_" + deckey + "_" + src.name + "_shotnoise"] = float(shotnoise)
	
#print "\nI would now update the database."
#proquest(askquestions)
print "\nI will now update the database."

backupfile(imgdb, dbbudir, "readout_"+deckey)


for field in newfields:
	if field["fieldname"] not in db.getFieldNames(imgdb):
		db.addFields(imgdb, ["%s:%s" % (field["fieldname"], field["type"])])

print "New fields added."


# The writing itself : here we will skip the duplicated reference.

widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, maxval=nbimg+2).start()

for i, image in enumerate(images[1:]): # we skip the duplicated reference.
	pbar.update(i)	
	db.update(imgdb, [deckeyfilenum], [image[deckeyfilenum]], image["updatedict"])
	
pbar.finish()

# As usual, we pack the db :
db.pack(imgdb)
# Note that it seems to be better to pack the database before "changing a changed" entry !

notify(computer, withsound, "The results of %s are now in the database." % deckey)



