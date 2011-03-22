"""

Histogram
We do one histogramm for every setname.
We do not look at the treatme flag, but instead of this we use all images that have a correct value
we respect gogogo

"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
#import variousfct
#import headerstuff
#import star
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.dates

db = KirbyBase()
allimages = db.select(imgdb, ["gogogo"], [True], returnType='dict', sortFields=['mjd'])
	
for fieldname in ["medcoeff", "skylevel", "seeing", "ell"]:


	images = [image for image in allimages if image[fieldname] > 0.0]
	print "%s : %i images" % (fieldname, len(images))
	usedsetnames = sorted(list(set([image['setname'] for image in images])))

	minval = np.min(np.array([image[fieldname] for image in images]))
	maxval = np.max(np.array([image[fieldname] for image in images]))
	print "min, max = %f, %f" % (minval, maxval)

	for usedsetname in usedsetnames :
	
		#print usedsetname
		setimages = [image for image in images if image["setname"] == usedsetname]
		telescopenames = sorted(list(set([image['telescopename'] for image in setimages])))
		values = np.array([image[fieldname] for image in setimages])
		plt.figure(figsize=(15,5))
	
		plt.hist(values, 500, range=(minval, maxval), facecolor='red', edgecolor="none", log=False)
		plt.xlabel("Field : %s" % (fieldname))
		plt.title("Setname : %s (Telescopes : %s), %i images." % (usedsetname, "+".join(telescopenames), len(setimages)))
	
		if savefigs:
			plotfilepath = os.path.join(plotdir, "histo_%s_%s.pdf" % (fieldname, usedsetname))
			plt.savefig(plotfilepath)
			print "Wrote %s" % (plotfilepath)
		else:
			plt.show()


