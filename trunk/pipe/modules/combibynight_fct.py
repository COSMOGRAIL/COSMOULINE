

# OLD VERSION, HAS BEEN REPLACED BY A MORE INTELLIGENT ONE
#def groupbynights(data):	# returns a list of "lists of dicts" taken in a single night
#				# data is a flat list of dicts from the database
#				# we will "unflatten" this list according to the julian dates
#				
#				# can be applied on all images, no need for special selection
#	import sys
#	import operator # for the sorting
#	
#	jd = map(lambda x:float(x['mjd']), data)
#	images = map(lambda x: x['imgname'], data)
#	
#	nbimg = len(images)
#	
#	# We sort the dicts by date
#	notsortedimages = []
#	for i in range(nbimg):
#		notsortedimages.append([jd[i], data[i]])
#	sortedimages = sorted(notsortedimages, key=operator.itemgetter(0))
#
#	# We build a new list containing the sublists of dicts
#	nighttable = []
#	thisnight = []
#	lastjd = sortedimages[0][0] - 0.001
#	for i in range(nbimg):
#		#print i
#		thisjd = sortedimages[i][0]
#		diffjd = thisjd - lastjd
#		if diffjd < 0.0:
#			print "Fatal error"
#			sys.exit()
#		if diffjd < 0.1:
#			thisnight.append(sortedimages[i][1])
#		else:
#			nighttable.append(thisnight) # seems to work (deep copy problem etc)
#			thisnight = []
#			thisnight.append(sortedimages[i][1])
#		lastjd = thisjd
#	nighttable.append(thisnight) # append the last thisnight
#		
#	return nighttable




def groupbynights(imagelist, separatesetnames=True):	# returns a list of "lists of dicts" taken in a single night,
						# and you can choose if you want to allow mixing setnames or not.
						# imagelist is a flat list of dicts from the database
						# we will "unflatten" this list according to the julian dates
				
						# can be applied on all images, no need for special selection or sorting.
	import sys
	import operator # for the sorting
	
	imagesbysets = []	# intermediary storage : we will put images in group of setnames in there, or all images.
	if separatesetnames:
		setnames = sorted(list(set([image["setname"] for image in imagelist])))
		for setname in setnames:
			thissetimages = [image for image in imagelist if image["setname"] == setname]
			imagesbysets.append(thissetimages)
			
	else:
		imagesbysets.append(imagelist)	# we simply put all images into the first list item.
		

	# And now we simply run our combination code individually on all the lists of imagesbysets.
	nighttable = []	# this is the big list we will return.
	
	for imageset in imagesbysets:
		
		jd = map(lambda x:float(x['mhjd']), imageset)
		#images = map(lambda x: x['imgname'], imageset)
	
		nbimg = len(imageset)
	
		# We sort the dicts by date
		notsortedimages = []
		for i in range(nbimg):
			notsortedimages.append([jd[i], imageset[i]])
		sortedimages = sorted(notsortedimages, key=operator.itemgetter(0))

		# We build a new list containing the sublists of dicts
		
		thisnight = []
		lastjd = sortedimages[0][0] - 0.001
		for i in range(nbimg):
			#print i
			thisjd = sortedimages[i][0]
			diffjd = thisjd - lastjd
			if diffjd < 0.0:
				print "Fatal error"
				sys.exit()
			if diffjd < 0.4:			# this will be the maximum gap between observations in one same night.
				thisnight.append(sortedimages[i][1])
			else:
				nighttable.append(thisnight[:]) # then we close the current night we make a deep copy just to be sure ...
				thisnight = []			# create a new one
				thisnight.append(sortedimages[i][1])	# and add our first image of the new night.
			lastjd = thisjd				# we get ready to analysis the new image.
		nighttable.append(thisnight) # append the last thisnight
		
	return nighttable	



def nightspan(night):	# returns the full span of time of the observations in that night
			# can be applied on all images
	if len(night) <= 1:
		return 0.0
	else:
		span = float(night[-1]['mjd']) - float(night[0]['mjd'])
		return span*24.00 # thransform to hours

def values(listofnights, key):	# stats of the values within the given nights

	from numpy import array, median, std, min, max, mean
	medvals=[]
	stddevvals=[]
	minvals=[]
	maxvals=[]
	meanvals = []
	for night in listofnights:
		values = array([float(image[key]) for image in night])
		medvals.append(median(values))
		stddevvals.append(std(values))
		minvals.append(min(values))
		maxvals.append(max(values))
		meanvals.append(mean(values))
	
	return {'median': medvals, 'stddev': stddevvals, 'min': minvals, 'max': maxvals, 'mean':meanvals}
	


def mags(listofnights, key):	# some stats of the mags within the given nights

	from numpy import array, asarray, log10, median, std, min, max, clip
	medvals=[]
	stddevvals=[]
	minvals=[]
	maxvals=[]
	uperrors=[]
	downerrors=[]
	for night in listofnights:
		#values = -2.5 * log10(asarray([float(image[key]) for image in night]))
		values = -2.5 * log10(clip(asarray([float(image[key]) for image in night]), 1.0, 1.0e18)) # We clip at 1.0, to avoid negative values
		medvals.append(median(values))
		stddevvals.append(std(values))
		minvals.append(min(values))
		maxvals.append(max(values))
		uperrors.append(maxvals[-1]-medvals[-1])
		downerrors.append(medvals[-1]-minvals[-1])
	
	return {'median': medvals, 'stddev': stddevvals, 'min': minvals, 'max': maxvals, 'up':uperrors, 'down':downerrors}



# THIS IS NOT USED ANYMORE, AS WE NOW DO EVERY RENORMALIZATION BEFORE THE DECONVOLUTION ITSELF !
#def renormmags(listofnights, key, renormfieldname): 	# Very similar to mags, but applies the renormalization coefficients
#							# Remeber : these are additive in magnitude for now !!!
#
#	from numpy import array, asarray, log10, median, std, min, max
#	medvals=[]
#	stddevvals=[]
#	minvals=[]
#	maxvals=[]
#	uperrors=[]
#	downerrors=[]
#	for night in listofnights:
#		values = -2.5 * log10(asarray([float(image[key]) for image in night]))
#		addmags = - asarray([float(image[renormfieldname]) for image in night])
#		values = values + addmags
#		medvals.append(median(values))
#		stddevvals.append(std(values))
#		minvals.append(min(values))
#		maxvals.append(max(values))
#		uperrors.append(maxvals[-1]-medvals[-1])
#		downerrors.append(medvals[-1]-minvals[-1])
#	
#	return {'median': medvals, 'stddev': stddevvals, 'min': minvals, 'max': maxvals, 'up':uperrors, 'down':downerrors}
#

