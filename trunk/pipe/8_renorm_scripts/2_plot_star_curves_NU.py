"""
Now that the coeffs are in the db, you might want to plot curves
(very similar to those made by the renormalize script), but for other stars,
not involved in the renormalization.
"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
import variousfct
import star
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates

print "I will plot lightcurves using renormalization coefficient called :"
print renormname
print "for the sources"
for renormsource in renormsources:
	print renormsource


db = KirbyBase()
allimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['mjd'])
print "%i images in total." % len(allimages)


for renormsource in renormsources:
	deckey = renormsource[0]
	sourcename = renormsource[1]
	print deckey
	
	deckeyfilenumfield = "decfilenum_" + deckey
	fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
	errorfieldname = "out_" + deckey + "_" + sourcename + "_shotnoise"
	decnormfieldname = "decnorm_" + deckey
	
	images = [image for image in allimages if image[deckeyfilenumfield] != None]
	print "%i images" % len(images)

	fluxes = np.array([image[fluxfieldname] for image in images])
	errors = np.array([image[errorfieldname] for image in images])
	decnormcoeffs = np.array([image[decnormfieldname] for image in images])
	airmasses = np.array([image["airmass"] for image in images])

	renormcoeffs = np.array([image[renormname] for image in images])
	
	renormfluxes = fluxes*renormcoeffs
	renormerrors = errors*renormcoeffs
	ref = np.median(renormfluxes)
	
	mhjds = np.array([image["mhjd"] for image in images])
	
	plt.figure(figsize=(15,15))

	#plt.errorbar(mhjds, renormfluxes/ref, yerr=renormerrors/ref, ecolor=(0.8, 0.8, 0.8), linestyle="None", marker=".")
	plt.errorbar(mhjds, renormfluxes/ref, yerr=renormerrors/ref, ecolor=(0.8, 0.8, 0.8), linestyle="None", marker="None")
	plt.scatter(mhjds, renormfluxes/ref, s=12, c=airmasses, vmin=1.0,vmax=1.5, edgecolors='none', zorder=20)
	

	plt.title("Source %s, %s, normalized with %s" % (sourcename, deckey, renormname))
	plt.xlabel("MHJD")
	plt.ylabel("Flux in electrons / median")
	plt.grid(True)
	plt.ylim(0.95, 1.05)
	plt.xlim(np.min(mhjds), np.max(mhjds))
	
	cbar = plt.colorbar(orientation='horizontal')
	cbar.set_label('Airmass') 

	if savefigs:
		plotfilepath = os.path.join(plotdir, "renorm_%s_renormflux_%s.pdf" % (renormname, sourcename))
		plt.savefig(plotfilepath)
		print "Wrote %s" % (plotfilepath)
	else:
		plt.show()
