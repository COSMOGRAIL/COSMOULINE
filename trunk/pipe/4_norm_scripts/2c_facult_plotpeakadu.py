
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np

import matplotlib.pyplot as plt


db = KirbyBase()
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')

nbrofimages = len(images)


# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print "Photom stars :"
print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])


for s in photomstars:
	
	plt.figure(figsize=(12,8))
	peakadus = np.array([image["%s_%s_peakadu" % (sexphotomname, s.name)] for image in images])
	
	n, bins, patches = plt.hist(peakadus, 1000, range=(0,67000), histtype='stepfilled', facecolor='grey')
	
	plt.title('Star %s peak value [ADU]' % (s.name), fontsize=18)
	#plt.show()
	plt.savefig(os.path.join(plotdir, "histo_%s_%s_peakadu.png" % (sexphotomname, s.name)))
	

