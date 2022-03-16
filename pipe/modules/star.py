"""

A class representing a source (star) on an image and some functions to play with stars.
This is made to be used in the context of sextractor catalogs, to align images, or two do photometry of non-aligned images.


Written for cosmouline, but can well be used alone : does not depend on any other cosmouline module.
This is by no way meant to be fast !

We need astroasciidata as soon as you try to read sextractor catalogs.
Otherwise just numpy.


Happy coding,
Malte

Overhaul : November 2010

"""


import sys, os
import math
import operator # For sorting
import copy

class Star:
	"""
	
	Often you will want to manipulate lists of such stars.
	
	"""


	def __init__(self, x=0.0, y=0.0, name="untitled", flux=-1.0, props={}, fwhm=-1.0, ell=-1.0):
		"""
		flux : Some "default" or "automatic" flux, might be a just good guess. Used for sorting etc.
		If you have several fluxes, colours, store them in the props dict.
		props : A dict to contain other properties of your choice (not required nor used by the methods).
		"""
		self.x = float(x)
		self.y = float(y)
		self.name = str(name)
		self.flux = float(flux)
		self.props = props
		self.fwhm = float(fwhm)
		self.ell = float(ell)
	
	def __getitem__(self, key) :
		"""
		Used for sorting list of stars.
		"""
		if key == 'flux':
			return self.flux
		if key == 'fwhm':
			return self.fwhm
		if key == 'ell':
			return self.ell
	
	def __str__(self):
		return "%10s : (%8.2f,%8.2f) | %12.2f | %5.2f %5.2f" % (self.name, self.x, self.y, self.flux, self.fwhm, self.ell)


	def shift(self, shift):
		"""
		shift is a tuple (x, y)
		"""
		self.x = self.x + shift[0]
		self.y = self.y + shift[1]
	
	def rotate(self, angle, center = (0, 0)):
		"""
		Plain rotation
		angle is in degrees, center is a tuple (x, y)
		"""
		
		anglerad = math.pi*angle/180.0
		rota = 	math.cos(anglerad)
		rotb = -math.sin(anglerad)
		rotc = -rotb
		rotd = rota
		xs = self.x - center[0]
		ys = self.y - center[1]
		us = rota*xs + rotb*ys
		vs = rotc*xs + rotd*ys
		self.x = us + center[0]
		self.y = vs + center[1]

	def zoom(self, scalingratio):
		self.x = self.x * scalingratio
		self.y = self.y * scalingratio

	def findshift(self, otherstar):
		"""
		returns the shift from self to the other stars, as a tuple
		i.e. "otherstar - self"
		"""
		return (otherstar.x - self.x, otherstar.y - self.y)
		
	def distance(self, otherstar):
		"""
		returns the distance between the two stars
		"""
		shift = self.findshift(otherstar)
		return math.sqrt(shift[0]*shift[0] + shift[1]*shift[1])

	def trigangle(self, otherstar):
		"""
		returns the "trigonometric" angle of the vector to go from
		self to the otherstar, in degrees
		"""
		return math.atan2(otherstar.y - self.y, otherstar.x - self.x) * (180.0/math.pi) % 360.0
		

	def distanceandsort(self, otherstarlist):
		"""
		returns a list of dicts(star, dist, origpos), sorted by distance to self.
		The 0th star is the closest.
		
		otherstarlist is not modified.
		"""
		import operator # for the sorting
		
		returnlist=[]
		for i, star in enumerate(otherstarlist):
			dist = self.distance(star)
			returnlist.append({'star':star, 'dist':dist, 'origpos':i})
		returnlist = sorted(returnlist, key=operator.itemgetter('dist')) # sort stars according to dist
		
		return returnlist

### And now some functions to manipulate list of such stars ###


def printlist(starlist):
	"""
	...
	"""
	for source in starlist:
		print source

def readmancat(mancatfilepath, verbose="True"):
	"""
	Reads a "manual" star catalog -- by manual, I mean "not written by sextractor".
	So this is typically a short file.
	
	Comment lines start with #, blank lines are ignored.
	The format of an actual data line is
	
	starname xpos ypos [flux]
	
	The data is returned as a list of star objects.
	"""
	
	if not os.path.isfile(mancatfilepath):	
		print "File does not exist :"
		print mancatfilepath
		print "Line format to write : starname xpos ypos [flux]"
		sys.exit(1)
		
	
	myfile = open(mancatfilepath, "r")
	lines = myfile.readlines()
	myfile.close
	
	table=[]
	knownnames = [] # We check for uniqueness of the names
	
	for i, line in enumerate(lines):
		if line[0] == '#' or len(line) < 4:
			continue
		elements = line.split()
		nbelements = len(elements)
		
		if nbelements != 3 and nbelements != 4:
			print "Format error on line", i+1, "of :"
			print mancatfilepath
			print "The line looks like this :"
			print line
			print "... but we want : starname xpos ypos [flux]"
			sys.exit(1)
		
		name = elements[0]
		x = float(elements[1])
		y = float(elements[2])
		if nbelements == 4:
			flux = float(elements[3])
		else:
			flux = -1.0	
		
		if name in knownnames:
			print "Error in %s" % (mancatfilepath)
			print "The name '%s' (line %i) is already taken." % (name, i+1)
			print "This is insane, bye !"
			sys.exit(1)
		knownnames.append(name)
		
		#table.append({"name":name, "x":x, "y":y, "flux":flux})
		table.append(Star(x=x, y=y, name=name, flux=flux))
	
		
	
	if verbose: print "I've read", len(table), "sources from", os.path.split(mancatfilepath)[1]
	return table


def readsexcat(sexcatfilepath, verbose=True, maxflag = 2, posflux = True, propfields=[]):
	"""
	We read a sextractor catalog with astroasciidata and return a list of stars.
	Minimal fields that must be present in the catalog :
		- NUMBER
		- X_IMAGE
		- Y_IMAGE
		- FWHM_IMAGE
		- ELLIPTICITY
		- FLUX_AUTO
		- FLAGS
		
	maxflag : maximum value of the FLAGS that you still want to keep. Sources with higher values will be skipped.
	FLAGS == 0 : all is fine
	FLAGS == 2 : the flux is blended with another one; further info in the sextractor manual.
	
	posflux : if True, only stars with positive FLUX_AUTO are included.
	
	propfields : list of FIELD NAMES to be added to the props of the stars.
	
	I will always add FLAGS as a propfield by default.
	
	"""
	import asciidata
	
	
	if not os.path.isfile(sexcatfilepath):
		print "Sextractor catalog does not exist :"
		print sexcatfilepath	
		sys.exit(1)
	
	returnlist = []
	
	if verbose : 
		print "Reading %s " % (os.path.split(sexcatfilepath)[1])
		
	mycat = asciidata.open(sexcatfilepath)
	
	# We check for the presence of required fields :
	minimalfields = ["NUMBER", "X_IMAGE", "Y_IMAGE", "FWHM_IMAGE", "ELLIPTICITY", "FLUX_AUTO", "FLAGS"]
	minimalfields.extend(propfields)
	availablefields = [col.colname for col in mycat]
	for field in minimalfields:
		if field not in availablefields:
			print "Field %s not available in your catalog file !" % (field)
			sys.exit(1)
	
	if verbose : 
		print "Number of sources in catalog : %i" % (mycat.nrows)
		
	propfields.append("FLAGS")
	propfields = list(set(propfields))
		
	if mycat.nrows == 0:
		if verbose :
			print "No stars in the catalog :-("
	else :
		for i, num in enumerate(mycat['NUMBER']) :
			if mycat['FLAGS'][i] > maxflag :
				continue
			flux = mycat['FLUX_AUTO'][i]
			if posflux and (flux < 0.0) :
				continue
			
			props = dict([[propfield, mycat[propfield][i]] for propfield in propfields])
			
			newstar = Star(x = mycat['X_IMAGE'][i], y = mycat['Y_IMAGE'][i], name = str(num), flux=flux,
					props = props, fwhm = mycat['FWHM_IMAGE'][i], ell = mycat['ELLIPTICITY'][i])
			
			returnlist.append(newstar)
	
	
	if verbose:
		print "I've selected %i sources" % (len(returnlist))
		
	return returnlist
	


def findstar(starlist, nametofind):
	"""
	Returns a list of stars for which name == nametofind
	"""
	foundstars = []
	for source in starlist:
		if source.name == nametofind:
			foundstars.append(source)
	return foundstars




	
def sortstarlistbyflux(starlist):
	"""
	starlist is a list of star instances, and we sort it
	according to flux : highest flux first
	"""
	sortedstarlist = sorted(starlist, key=operator.itemgetter('flux'))
	sortedstarlist.reverse()
	return sortedstarlist

def sortstarlistby(starlist, measure):
	"""
	starlist is a list of star instances, and we sort it
	according to the star obejct attribute measure : lowest first
	
	measure = flux, fwhm, ell
	
	"""
	sortedstarlist = sorted(starlist, key=operator.itemgetter(measure))
	return sortedstarlist


def rotatestarlist(starlist, degrees, center):
	for star in starlist:
		star.rotate(degrees, center)
		
def shiftstarlist(starlist, shifttuple):
	for star in starlist:
		star.shift(shifttuple)

def zoomstarlist(starlist, scalingratio):
	for star in starlist:
		star.zoom(scalingratio)



def formpairs(starlist1, starlist2, tolerance = 2.0, onlysingle = False, transform = False, scalingratio = 1.0, angle = 0.0, shift = (0.0, 0.0), verbose = True):
	"""
	starlist1 and starlist2 are two lists of stars.
	For each star in starlist1, we find the closest star of starlist2, if found within a given tolerance.
	starlist1 = hand picked stars
	starlist2 = large catalog of 
	We return a list of pairs of the corresponding stars (in form of a dict). See first lines to get that.
	
	transform == True :
		starlist2 is tranformed, using scalingration, angle, and shift, prior to the pair creation.
		Nevertheless, the idlist 2 will be filled with the raw untransformed stars from starlist2 !!!
		
	
	tolerance = maximum distance between identified stars. Set it high -> simply select the closest one.
	onlysingle == False : closest star within tolerance
	onlysingle == True : same, but only if no other star is within tolerance
	
	"""
	idlist1 = [] # Stars of starlist1 identified in starlist2
	idlist2 = [] # The corresponding starlist2 stars (same number, same order)
	iddists = [] # The list of distances between the stars of idlist1 and idlist2 (same number and order)
	nomatch = [] # Stars of starlist1 that could not be identified in starlist2
	notsure = [] # Stars of starlist1 that could not doubtlessly be identified in starlist2
	
	
	# If required, we transform the starlist 2 :
	if transform :
		transtarlist2 = copy.deepcopy(starlist2)
		zoomstarlist(transtarlist2, scalingratio)
		rotatestarlist(transtarlist2, angle, (0, 0))
		shiftstarlist(transtarlist2, shift)
		# Remember : we will pick the stars to fill idlist2 from the raw starlist2 !
	
	else:
		transtarlist2 = starlist2
	
	returndict = {"idlist1":idlist1, "idlist2":idlist2, "iddists":iddists, "nomatch":nomatch, "notsure":notsure}
	
	if len(starlist1) == 0:
		if verbose :
			print "Your starlist1 is empty, nothing to do."
		return returndict
	
	if len(transtarlist2) == 0:
		if verbose :
			print "Your starlist2 is empty, no stars to identify."
		nomatch.extend(starlist1)
		return returndict
			
	# Special treatment in the case there is only one star in starlist2
	if len(transtarlist2) == 1:
		if verbose :
			print "Your starlist2 is quite small..."
		for handstar in starlist1:
			closest = handstar.distanceandsort(transtarlist2)
			if closest[0]['dist'] > tolerance:
				if verbose :
					print "No match for star %s" % handstar.name
				nomatch.append(handstar)
				continue
			else:
				idlist1.append(handstar)
				idlist2.append(starlist2[closest[0]['origpos']])
				iddists.append(closest[0]['dist'])
		
		return returndict
				
	# The usual case :
	else:	
		for handstar in starlist1:
			closest = handstar.distanceandsort(transtarlist2)
			if closest[0]['dist'] > tolerance:
				if verbose :
					print "No match for star %s" % handstar.name
				nomatch.append(handstar)
				continue
				
			# Ok, then it must be closer then tolerance. We check for other stars whose distance is less then tolerance different from the first ones distance :
			elif onlysingle and (closest[1]['dist'] - closest[0]['dist'] < tolerance):
				if verbose :
					print "Multiple candidates for star %s, skipping" % handstar.name
				notsure.append(handstar)
				continue
			
			# Finally, this means we have found our star
			else:
				idlist1.append(handstar)
				idlist2.append(starlist2[closest[0]['origpos']])
				iddists.append(closest[0]['dist'])
	
		return returndict
	


def listidentify(starlist1, starlist2, tolerance = 2.0, onlysingle = False, transform = False, scalingratio = 1.0, angle = 0.0, shift = (0.0, 0.0), verbose = True):
	"""
	Same as formpairs (we call it), but we return only the idlist2 (not transformed, even if you give a transform), but with names taken from idlist1.
	Typical : starlist2 is a sextractor catalog with random names, starlist 1 is a handpicked catalog with special names,
	and you want to get stars with sextractor properties but your own names.
	"""
	
	formpairsdict = formpairs(starlist1, starlist2, tolerance = tolerance, onlysingle = onlysingle, transform = transform, scalingratio = scalingratio, angle = angle, shift = shift, verbose = verbose)
	
	match = []
	
	for (s1, s2, d) in zip(formpairsdict["idlist1"], formpairsdict["idlist2"], formpairsdict["iddists"]):
		s2.name = s1.name
		s2.props["iddist"] = d
		match.append(s2)
		
	nomatchnames = [s.name for s in formpairsdict["nomatch"]]
	notsurenames = [s.name for s in formpairsdict["notsure"]]
	
	return {"match":match, "nomatchnames":nomatchnames, "notsurenames":notsurenames}

	


def findtrans(preciserefmanstars, autostars, scalingratio = 1.0, tolerance = 2.0, minnbrstars = 5, mindist = 100.0, nref = 10, nauto = 30, verbose=True):
	
	"""
	Finds a rotation and shift between two catalogs (a big dirty one and a small handpicked one).
	Both catalogs should be SORTED IN FLUX, and the second one should be smaller for max performance.
	
	Only the first nref stars of preciserefmanstars are considered for searching the possible matches, and furthermore only 
	pairs farther then mindist are considered.
	
	tolerance is used when looking if a match was found.
	
	minnbrstars = as soon as this number of stars are identified, the algo stops, we look no further.
	
	The scalingratio parameter is a float to multiply with a distance of the autostars to match the same distance between the preciserefmanstars.
	
	We return a dict of 3 things :
	- nbr of identified stars (-1 if failed)
	- rotation angle (center = 0,0)
	- shift
	
	This should then be used to transform your autostars, and then run listidentify between the catalogs if you want ...
	This is done with the function formpairs
	
	"""
	
	# Think of a Hubble expansion with "origin" (0,0)
	# We apply this to the image to align, so that it matches the distances in the reference image.
	autostarscopy = copy.deepcopy(autostars)
	zoomstarlist(autostarscopy, scalingratio)
	
	n = 0 # a counter for the number of tries
	indentlist = [] # only used in case of failure
	
	for b, brightstar in enumerate(preciserefmanstars[:nref]):
		for f, faintstar in enumerate(preciserefmanstars[:nref]):
			if f == b: continue
			stardistance = brightstar.distance(faintstar)
			if stardistance < mindist : continue

			# We have a pair of stars from the preciserefmancat.
			# Let's see if we find to stars in the autocat with a similar distance.
			
			for bc, brightcandidate in enumerate(autostarscopy[:nauto]):
				for fc, faintcandidate in enumerate(autostarscopy[:nauto]):
					if fc == bc: continue
					candidatedistance =  brightcandidate.distance(faintcandidate)
					if math.fabs(candidatedistance - stardistance)/stardistance > 0.05 :
						# So if there is a disagreement larger then 5 percent...
						continue
					
					# We now have a promising pair of pairs, let's check them out.
					
					n = n+1
					
					starangle = brightstar.trigangle(faintstar)
					candidateangle = brightcandidate.trigangle(faintcandidate)
					rotcandangle = (starangle - candidateangle) % 360.0	# value to "add" to cand to match the star
					
					# We apply this rotation to the bright candidate, to determine the shift :
					testcand = copy.deepcopy(brightcandidate)
					testcand.rotate(rotcandangle, (0, 0))
					candshift = testcand.findshift(brightstar)
					
					# We apply the rotation and this shift to the full zoomed autostarlist :
					testcandlist = copy.deepcopy(autostarscopy)
					rotatestarlist(testcandlist, rotcandangle, (0, 0))
					shiftstarlist(testcandlist, candshift)
					
					# We evaluate the match between the transformed autostars and the ref stars :
					
					pairsdict = formpairs(preciserefmanstars, testcandlist, tolerance = tolerance, onlysingle = True, verbose = False)
					nbrids = len(pairsdict["idlist1"])
					indentlist.append(nbrids)
					
					if nbrids >= minnbrstars:
						# We got it !
						
						if verbose :
							print "Number of tries : %i" % n
							print "Distance difference : %.2f pixels" % math.fabs(candidatedistance - stardistance)
							print "Candidate rotation angle : %.2f degrees" % rotcandangle
							
							print "Star pairs used :"
							print brightstar
							print faintstar
							print brightcandidate
							print faintcandidate
							
							print "Identified stars : %i / %i" % (nbrids, len(preciserefmanstars) )

						return {"nbrids":nbrids, "angle":rotcandangle, "shift":candshift}

	
	if verbose :
		print "I'm a superhero, but I failed"
	if len(indentlist) > 0:
		if verbose :
			print "Maximum identified stars : %i" % max(indentlist)
			
	return {"nbrids":-1, "angle":0.0, "shift":(0.0, 0.0)}
					


def writeforgeomap(filename, pairs):
	"""
	Writes an input catalog of corresponding star pairs, for geomap
	Pair is a list of couples like (refstar, startoalign)
	"""


	import csv
	
	table = []	
	for pair in pairs:
		table.append([pair[0].x, pair[0].y, pair[1].x, pair[1].y])

	geomap = open(filename, "wb") # b needed for csv
	writer = csv.writer(geomap, delimiter="\t")
	writer.writerows(table)
	geomap.close()


