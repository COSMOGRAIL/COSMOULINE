
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np

import matplotlib.pyplot as plt


db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields = ["mhjd"])

if update:
	askquestions = False
nbrofimages = len(images)
print "I respect treatme, and selected only %i images" % (nbrofimages)

# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print "Photom stars :"
print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])



nbrofimages = len(images)
print "I respect treatme and will treat", nbrofimages, "images."
proquest(askquestions)


mhjds = np.array([image["mhjd"] for image in images])
medcoeffs = np.array([image["medcoeff"] for image in images])



def plotdevs(fluxes, label, color):
	nonepos = np.isnan(fluxes)
	print "%i images without flux measure." % (np.sum(nonepos))
	fluxes[nonepos] = 0.0
	normflux = np.median(fluxes * medcoeffs)
	normdevs = (fluxes * medcoeffs) / normflux
	normdevs[nonepos] = None
	ax1.plot(mhjds, normdevs, linestyle="None", marker=".", color = color, label = label)
	


for s in photomstars :
	
	
	print "Star %s" % (s.name)
	
	plt.figure(figsize=(12,8))
	plt.title("Star %s" % (s.name))
	ax1 = plt.gca()
	ax2 = ax1.twinx()
	

	print images[5]
	
	# The specifictaion of dtype is important, toherwise the None produce crap.
	autofluxes = np.array([image["%s_%s_auto_flux" % (sexphotomname, s.name)] for image in images], np.float64)
	ap30fluxes = np.array([image["%s_%s_ap30_flux" % (sexphotomname, s.name)] for image in images], np.float64)
	ap90fluxes = np.array([image["%s_%s_ap90_flux" % (sexphotomname, s.name)] for image in images], np.float64)
	
	plotdevs(ap90fluxes, "ap90", "blue")
	plotdevs(ap30fluxes, "ap30", "red")
	plotdevs(autofluxes, "auto", "black")
	
	ax1.set_ylim((0.78, 1.22))
	ax1.set_ylabel("Flux * medcoeff / median")
	ax1.set_xlabel("MHJD")
	ax1.legend()
	
	ax2.plot(mhjds, medcoeffs, "gray")
	for tl in ax2.get_yticklabels():
    		tl.set_color('gray')
	ax2.set_ylim((0.1, 2.9))
	ax2.set_ylabel("medcoeff", color="gray")
	
	if savefigs:
		plotfilepath = os.path.join(plotdir, "sexphotom_%s_%s_fluxes.pdf" % (sexphotomname, s.name))
		plt.savefig(plotfilepath)
		print "Wrote %s" % (plotfilepath)
	else:
		plt.show()

	




