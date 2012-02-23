"""
Look for strange flux values...

"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np
import matplotlib.pyplot as plt
import shutil


figbase = deckey


db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mhjd'])

ptsrcs = star.readmancat(ptsrccat)
nbptsrcs = len(ptsrcs)
print "Number of point sources :", nbptsrcs
print "Names of sources : "
for src in ptsrcs: print src.name





for src in ptsrcs:

	fluxfieldname = "out_" + deckey + "_" + src.name + "_flux"
	noisefieldname = "out_" + deckey + "_" + src.name + "_shotnoise"
	decnormfieldname = "decnorm_" + deckey
	
	fluxes = np.array([image[fluxfieldname] for image in images])
	decnormcoeffs = np.array([image[decnormfieldname] for image in images])
	
	normfluxes = fluxes*decnormcoeffs
	
	"""
	for i, flux in enumerate(fluxes):
		if flux < 0.0:
			print "Negative flux: %.3f " % (flux)
			
	for i, norm in enumerate(decnormcoeffs):
		if norm < 0.0:
			print "Negative normcoeff: %.3f " % (norm)
			
	for i, normflux in enumerate(normfluxes):
		if normflux < 0.0:
			print "Negative normalized flux: %.3f " % (normflux)
	"""
	
	rejlines = []	
	rejectimages = [image for image in images if image[fluxfieldname] < 0.0]
	rejlines.extend("%s\t\t%s" % (image["imgname"], "flux = %.3f" % image[fluxfieldname]) for image in rejectimages)
	rejectimages = [image for image in images if image[decnormfieldname] < 0.0]
	rejlines.extend("%s\t\t%s" % (image["imgname"], "normcoeff = %.3f" % image[decnormfieldname]) for image in rejectimages)
	
	if len(rejlines) == 0:
		print "All images have positive fluxes and normcoefficients."
	
	else:
		print "These images have negative fluxes and / or a negative normcoefficient:"
		print "\n".join(rejlines)
		print "Please put them on your kicklist!"
	
