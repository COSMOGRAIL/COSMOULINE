#
#	Histogramm of the measured seeings, for each set.
#

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from pylab import * # matplotlib and NumPy etc

#imgdb = "/Users/mtewes/Desktop/vieuxdb.dat"

db = KirbyBase()

# We read this only once.
images = db.select(imgdb, ['gogogo'], [True], returnType='dict')

usedsetnames = list(set([image['setname'] for image in images]))

nsets = len(usedsetnames)
figure(figsize=(6,1.4*nsets))	# set figure size

maxval = max(array([image['geomaprms'] for image in images]))
print "maximum value is :", maxval
maxrange = 1.2

for i, name in enumerate(usedsetnames):

	# We extract the seeing values for this setname
	vect = array([image['geomaprms'] for image in images if image['setname'] == name])
	print "%20s : %4i" %(name, len(vect))
	
	sub = 0.06+i*(0.88/nsets ) # relative position of the x axis on the figure.
	ax = axes([0.08, sub, 0.85, 0.78/nsets])
	
	# Write the setname on the graph
	ax.annotate(name, xy=(0.8, 0.7),  xycoords='axes fraction')
	
	if i > 0:	# hide labels
		ax.set_xticklabels([])
        else:
        	xlabel("geomaprms [pixel]")
        	
	n, bins, patches = hist(vect, 100, range=(0.0,maxrange), histtype='stepfilled', facecolor='grey')
	
	for tick in ax.yaxis.get_major_ticks(): # reduce the label fontsize.
		tick.label1.set_fontsize(8)

	
	# to share a common x axis interactively :
	#if i == 0:	
	#	#xlabel("geomaprms [pixels]")	# show labels
	#	ax1 = axes([0.08, sub, 0.85, 0.78/nsets])
	#	ax1.annotate(name, xy=(0.8, 0.7),  xycoords='axes fraction') # Write the setname on the graph
	#	for tick in ax1.yaxis.get_major_ticks(): # reduce the label fontsize.
	#		tick.label1.set_fontsize(8)
        #else:
        #	ax = axes([0.08, sub, 0.85, 0.78/nsets], sharex=ax1)
        #	
        #	ax.annotate(name, xy=(0.8, 0.7),  xycoords='axes fraction') # Write the setname on the graph
        #	for tick in ax.yaxis.get_major_ticks(): # reduce the label fontsize.
	#		tick.label1.set_fontsize(8)
	#	ax.set_xticklabels([])		# hide labels	

title('geomaprms histogram', fontsize=18)
show()
	
