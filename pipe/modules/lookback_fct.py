from numpy import *
import matplotlib.pyplot as plt




def posplotbydate(images, image, deckey, ptsrc, filename, maglims = None):
	# images is the list of dicts of all images *of this deconcvolution* to be plotted as "background" points
	# image is that particular image (as a dict from the database) you want to highlight
	# deckey is the deckey, ptsrc is the list of source names : they are used to find the intensity fieldnames
	# filename is the path to the png to save
	# maglims is an optional list like (-12.7, -11.7) to impose graph limits instead of min max.
	
	
	plt.figure(figsize=(12,8))	# sets figure size
	axes = plt.gca()
	figure = plt.gcf()
	figure.set_size_inches((8, 5))
	#figure.patch.set_alpha(0.0)	# make background transparent
		
	maglist = []
	mhjdlist = []
	for source in ptsrc:
	
		fluxfieldname = 'out_'+deckey+'_'+ source +'_flux'
	
		mags = -2.5 * log10(clip(asarray([x[fluxfieldname] for x in images]), 1.0, 1.0e18))
		mhjds = asarray([x["mhjd"] for x in images])
	
		maglist.append(mags)
		mhjdlist.append(mhjds)
	
	mags = concatenate(maglist)
	mhjds = concatenate(mhjdlist)

	plt.plot(mhjds, mags, color="#AAAAAA", marker=".", linestyle="None")
	
	# We draw the points from the present set on top of that :
	
	maglist = []
	mhjdlist = []
	for source in ptsrc:
	
		fluxfieldname = 'out_'+deckey+'_'+ source +'_flux'
	
		mags = -2.5 * log10(clip(asarray([x[fluxfieldname] for x in [x for x in images if x["setname"] == image["setname"]]]), 1.0, 1.0e18))
		mhjds = asarray([x["mhjd"] for x in [x for x in images if x["setname"] == image["setname"]]])
	
		maglist.append(mags)
		mhjdlist.append(mhjds)
	
	mags = concatenate(maglist)
	mhjds = concatenate(mhjdlist)

	plt.plot(mhjds, mags, color="#000000", marker=".", linestyle="None")
	
	
	# Now we add the particular points from the present image, in colour
	
	for source in ptsrc:
	
		fluxfieldname = 'out_'+deckey+'_'+ source +'_flux'
		
		mag = -2.5 * log10(clip(asarray([image[fluxfieldname]]), 1.0, 1.0e18))
		mhjd = asarray([image["mhjd"]])
	
		plt.plot(mhjd, mag, marker=".", linestyle="None", color="red", markersize = 15)
		axes.annotate(source, (mhjd, mag), xytext=(7, -6), textcoords='offset points',size=12, color="red")
			
	# reverse y axis for magnitudes :
	
	if maglims:
		plt.ylim(maglims)

	axes.set_ylim(axes.get_ylim()[::-1])
	
	plt.title("Overview", fontsize=20)
	plt.xlabel('mhjd [days]')
	plt.ylabel('Magnitude')
	plt.grid(True)
	
	#plt.show()
	plt.savefig(filename, dpi = 72, transparent=True)
	
	axes.images = []	# THIS IS CRUCIAL TO PREVENT A MEMORY LEAKAGE (PERHAPS A BUG ...)
	plt.close('all')
	
	
	
def posplotbyimg(images, nightlims, image, deckey, ptsrc, filename, maglims = None):
	
	# We plot all points, image by image, and rely on the ordering by setname + mhjd to add some indicators for nights.
	
	# same parameters as above, plus
	# nightlims, a simple array giving the positions of night limits, typically build with :
	#	nights = groupbynights(images, separatesetnames=True)
	#	nightlengths = map(len, nights)
	#	nightlims = add.accumulate(array(nightlengths)) + 0.5

	
	
	plt.figure(figsize=(12,8))	# sets figure size
	axes = plt.gca()
	figure = plt.gcf()
	figure.set_size_inches((8, 5))
	#figure.patch.set_alpha(0.0)	# make background transparent
	
				
	
	# "All" points
	maglist = []
	numlist = []
	for source in ptsrc:

		fluxfieldname = 'out_'+deckey+'_'+ source +'_flux'
	
		mags = -2.5 * log10(clip(asarray([x[fluxfieldname] for x in images]), 1.0, 1.0e18))
		nums = arange(len(mags)) +1
	
		maglist.append(mags)
		numlist.append(nums)
	
	mags = concatenate(maglist)
	nums = concatenate(numlist)

	plt.plot(nums, mags, color="#AAAAAA", marker=".", linestyle="None")
	
	# "Vertical lines to separate nights"
	
	
	for lim in nightlims:
		plt.axvline(lim, color="#FF0000")
	
		
	# Now we add the particular points from the present image, in colour
	
	for source in ptsrc:
	
		fluxfieldname = 'out_'+deckey+'_'+ source +'_flux'
		
		mag = -2.5 * log10(clip(asarray([image[fluxfieldname]]), 1.0, 1.0e18))
		imagepos = [x["imgname"] for x in images].index(image["imgname"]) +1
		num = array([imagepos])
		
		plt.plot(num, mag, marker=".", linestyle="None", color="red", markersize = 15)
		axes.annotate(source, (num, mag), xytext=(7, -6), textcoords='offset points',size=12, color="red")
	
	# The plot limits :
	if maglims == "Sigma":
		# We try some sigma rejection ...
		center = median(mags)
		yinf = center - 2.0 * std(mags)
		ysup = center + 2.0 * std(mags)
		plt.ylim(yinf, ysup)
	elif maglims != None :
		plt.ylim(maglims)
	
	# reverse y axis for magnitudes :
	axes.set_ylim(axes.get_ylim()[::-1])
	plt.xlim((imagepos-10, imagepos+10))

	plt.title("Zoom on %s" % image["setname"], fontsize=20)
	plt.xlabel('Image')
	plt.ylabel('Magnitude')
	plt.grid(True)
	
	#plt.show()
	plt.savefig(filename, dpi = 72, transparent=True)	

	axes.images = []	# THIS IS CRUCIAL TO PREVENT A MEMORY LEAKAGE (PERHAPS A BUG ...)
	plt.close('all')

