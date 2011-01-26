execfile("../config.py")
from kirbybase import KirbyBase, KBError
import variousfct
#from readandreplace_fct import *
import star
#import progressbar
import numpy as np
import scipy
import f2n




db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True)

# We add the new fields :
ptsrc = star.readmancat(ptsrccat)
newfields = [{"fieldname": "out_" + deckey + "_" + s.name + "_randerror", "type": "float"} for s in ptsrc]
for field in newfields:
	if field["fieldname"] not in db.getFieldNames(imgdb):
		db.addFields(imgdb, ["%s:%s" % (field["fieldname"], field["type"])])


for i, image in enumerate(images):
	
	print "- " * 30
	print i, image["imgname"]
	
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
	
	#print "Sum of PSF : %.6f" % np.sum(psf)
	
	# We rebin it, 2x2 :
	psf = 4.0*f2n.rebin(smallpixpsf, (64, 64))
	
	#print "Sum of PSF : %.6f" % np.sum(psf)
	
	# We calculate the sharpness :
	sharpness = np.sum(psf * psf)
	
	print "Equivalent pixels : %.2f" % float(1.0/sharpness)
	
	image["updatedict"] = {}
	for s in ptsrc:
		# We get the flux, in electrons, as obtained by a deconv :
		flux = image["out_" + deckey + "_" + s.name + "_flux"]
		
		# We calculate the "optimal" error for psf fitting, as taken from here :
		# http://www.stsci.edu/hst/observatory/etcs/etc_user_guide/1_3_optimal_snr.html
		
		error = float(np.sqrt(flux + ((image["skylevel"] + image["readnoise"]**2.0)/sharpness)))
	
		print "\t%s : \t%9.2f +/- %5.2f %%" % (s.name, flux, 100*error/flux)
		
		image["updatedict"]["out_" + deckey + "_" + s.name + "_randerror"] = error
	
	db.update(imgdb, [deckeyfilenum], [image[deckeyfilenum]], image["updatedict"])
	
	# The sharpness of the samll pix psf :
	#smallsharpness = np.sum(smallpixpsf * smallpixpsf)
	#print sharpness
	#print smallsharpness
	#print sharpness/smallsharpness
	#variousfct.tofits("mcs.fits", ramcspsf, verbose=False)
	#variousfct.tofits("psf.fits", psf, verbose=False)

	
print "- " * 30
# As usual, we pack the db :
db.pack(imgdb)
