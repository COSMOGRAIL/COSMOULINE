#
#	Histogramm of the measured seeings, for each set.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *

import matplotlib.pyplot as plt
import numpy as np

#imgdb = "/Users/mtewes/Desktop/vieuxdb.dat"

db = KirbyBase()

# We read this only once.
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')

usedtelescopenames = list(set([image['telescopename'] for image in images]))



for i, name in enumerate(usedtelescopenames):

	# We extract the seeing values for this setname
	seeingvect = np.array([image['seeing'] for image in images if image['telescopename'] == name])
	print "%20s : %4i" %(name, len(seeingvect))
	
	plt.figure(figsize=(6, 3))
	
	n, bins, patches = plt.hist(seeingvect, 50, range=(0.5,3.5), histtype='stepfilled', facecolor='grey')

	plt.title('')
	plt.show()
	
