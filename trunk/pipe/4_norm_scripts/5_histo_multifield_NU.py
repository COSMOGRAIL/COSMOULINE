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
	
for (fieldname, plotrange) in [("medcoeff", [0.5, 3.0]), ("skylevel", [0.0, 10000.0]), ("seeing", [0.5, 3.0]), ("ell", [0.0, 0.5])]:


	images = [image for image in allimages if image[fieldname] > 0.0]
	print "%s : %i images" % (fieldname, len(images))
	usedsetnames = sorted(list(set([image['setname'] for image in images])))

	#minval = np.min(np.array([image[fieldname] for image in images]))
	#maxval = np.max(np.array([image[fieldname] for image in images]))
	#minmaxtext = "min, max = %f, %f" % (minval, maxval)
	#print minmaxtext
	
	for usedsetname in usedsetnames :
	
		print "Set ", usedsetname
		setimages = [image for image in images if image["setname"] == usedsetname]
		
		setminval = np.min(np.array([image[fieldname] for image in setimages]))
		setmaxval = np.max(np.array([image[fieldname] for image in setimages]))
		setminmaxtext = "min, max = %f, %f" % (setminval, setmaxval)
		print setminmaxtext
	
		telescopenames = sorted(list(set([image['telescopename'] for image in setimages])))
		values = np.array([image[fieldname] for image in setimages])
		plt.figure(figsize=(15,5))
	
		#plt.hist(values, 500, range=(minval, maxval), facecolor='red', edgecolor="none", log=False)
		plt.hist(values, 300, range=(plotrange[0], plotrange[1]), facecolor='red', edgecolor="none", log=False)
		plt.xlim(plotrange[0], plotrange[1])
		
		plt.xlabel("Field : %s       (%s)" % (fieldname, setminmaxtext))
		plt.title("Setname : %s (Telescopes : %s), %i images." % (usedsetname, "+".join(telescopenames), len(setimages)))
	
		if savefigs:
			plotfilepath = os.path.join(plotdir, "histo_%s_%s.pdf" % (fieldname, usedsetname))
			plt.savefig(plotfilepath)
			print "Wrote %s" % (plotfilepath)
			plt.close()
		else:
			plt.show()


