import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import configdir, imgdb, settings, plotdir
from modules.kirbybase import KirbyBase
from modules import star

askquestions = settings['askquestions']
sexphotomname = settings['sexphotomname']

import matplotlib.pyplot as plt


db = KirbyBase()

images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')
nbrofimages = len(images)


print("I respect treatme, and selected only %i images" % (nbrofimages))


# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print("Photom stars :")
#print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])


for s in photomstars:
	
	plt.figure(figsize=(12,8))
	peakadus = np.array([image["%s_%s_peakadu" % (sexphotomname, s.name)] for image in images])
	
	n, bins, patches = plt.hist(peakadus, 1000, range=(0,67000), histtype='stepfilled', facecolor='grey')
	
	medianpeak = float(np.median(peakadus))
	print(s.name, medianpeak)
	
	#axes = plt.gca()
	plt.axvline(x = medianpeak, color="red")

	plt.title("Star %s, median = %.2f" % (s.name, medianpeak))
	plt.xlabel('Peak value including sky [ADU]', fontsize=18)
	
	
	
	if settings['savefigs']:
		plotfilepath = os.path.join(plotdir, "%s_%s_peakaduhist.pdf" % (sexphotomname, s.name))
		plt.savefig(plotfilepath)
		print("Wrote %s" % (plotfilepath))
		plt.close()
	else:
		plt.show()

	
