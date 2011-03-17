
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np

import matplotlib.pyplot as plt


db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "I respect treatme, and selected only %i images" % (nbrofimages)


# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print "Photom stars :"
#print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])


for s in photomstars:
	
	plt.figure(figsize=(12,8))
	peakadus = np.array([image["%s_%s_peakadu" % (sexphotomname, s.name)] for image in images])
	
	n, bins, patches = plt.hist(peakadus, 1000, range=(0,67000), histtype='stepfilled', facecolor='grey')
	
	medianpeak = float(np.median(peakadus))
	print s.name, medianpeak
	
	#axes = plt.gca()
	plt.axvline(x = medianpeak, color="red")

	plt.title("Star %s, median = %.2f" % (s.name, medianpeak))
	plt.xlabel('Peak value including sky [ADU]', fontsize=18)
	
	
	
	if savefigs:
		plotfilepath = os.path.join(plotdir, "%s_%s_peakaduhist.pdf" % (sexphotomname, s.name))
		plt.savefig(plotfilepath)
		print "Wrote %s" % (plotfilepath)
	else:
		plt.show()

	
