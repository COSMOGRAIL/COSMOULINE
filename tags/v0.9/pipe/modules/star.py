#
#	Everything around the new "star class"
#	Useful for playing with star catalogues
#


class star:
	def __init__(self, x, y, name="NoName", flux=-1.0, fwhm=-1.0, ell=-1.0):
		self.x = float(x)
		self.y = float(y)
		self.name = str(name)
		self.flux = float(flux)
		self.fwhm = float(fwhm)
		self.ell = float(ell)
	
	def __getitem__(self, key): # we need this just for the sorting
		if key == 'flux':
			return self.flux
		if key == 'fwhm':
			return self.fwhm
		if key == 'ell':
			return self.ell

				
	def write(self):
		print "%10s : (%8.2f,%8.2f) | %12.2f | %5.2f %5.2f" % (self.name, self.x, self.y, self.flux, self.fwhm, self.ell)

	def shift(self, shift):
		"""shift is a tuple (x, y)"""
		self.x = self.x + shift[0]
		self.y = self.y + shift[1]
	
	def rotate(self, angle, center):
		"""imagine a matrix like rotation
		angle is in degrees, center is a tuple (x, y)"""
		import math
		
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
		"""returns the shift from self to the other stars, as a tuple
		i.e. "argument - self" """
		myshift = (otherstar.x - self.x, otherstar.y - self.y)
		return myshift
	
	def distance(self, otherstar):
		"""returns the distance between the two stars"""
		import math
		shift = self.findshift(otherstar)
		distance = math.sqrt(shift[0]*shift[0] + shift[1]*shift[1])
		return distance

	def trigangle(self, otherstar):
		"""returns the trigonometric angle of the vector to go from
		self to the other star, in degrees"""
		import math
		angle = math.atan2(otherstar.y - self.y, otherstar.x - self.x) * (180.0/math.pi) % 360.0
		#print rad/math.pi
		# * (180.0/math.pi) % 360.0
		return angle

	def distanceandsort(self, otherstarlist):
		"""returns a list of dicts(star, dist, origpos), sorted by distance to self.
		The 0th star is the closest."""
		import operator # for the sorting
		
		returnlist=[]
		for i, star in enumerate(otherstarlist):
			dist = self.distance(star)
			returnlist.append({'star':star, 'dist':dist, 'origpos':i})
		returnlist = sorted(returnlist, key=operator.itemgetter('dist')) # sort stars according to dist
		
		return returnlist


def findstar(starlist, nametofind):
	"""returns a list of stars for which name == nametofind"""
	foundstars = []
	for source in starlist:
		if source.name == nametofind:
			foundstars.append(source)
	return foundstars


def readmancatasstars(mancatfile):
	"""We call readmancat and return a list of star instances
	instead of a list of dicts"""
	from variousfct import readmancat
	returnlist = []
	rawlist = readmancat(mancatfile)
	for el in rawlist:
		returnlist.append(star(el['x'], el['y'], el['name'], el['flux']))
	return returnlist

def readsexcatasstars(sexcatfile):
	"""We read a sextractor catalog with astroasciidata and return
	a list of star instances"""
	import asciidata
	import os
	import sys
	if not os.path.isfile(sexcatfile):
		print "Sextractor catalog does not exist :"
		print sexcatfile	
		sys.exit()
	returnlist = []
	mycat = asciidata.open(sexcatfile)
	print "Number of sources in catalog :", mycat.nrows
	if mycat.nrows == 0:
		print "No stars in the catalog :-("
	else :
		for i, num in enumerate(mycat['NUMBER']):
			if (mycat['FLAGS'][i] == 0 or mycat['FLAGS'][i] == 2) and mycat['FWHM_IMAGE'][i] > 0.01 and mycat['FLUX_APER'][i] > 0.0:
			# Sextractor FLAG == 2 means that the flux is blended with another one.
			# For the alignement, a background galaxy is not a problem...
			#if mycat['FLAGS'][i] == 0 and mycat['FWHM_IMAGE'][i] > 0.01 and mycat['FLUX_APER'][i] > 0.0:
				returnlist.append(star(mycat['X_IMAGE'][i], mycat['Y_IMAGE'][i], str(num), mycat['FLUX_APER'][i], mycat['FWHM_IMAGE'][i], mycat['ELLIPTICITY'][i]))
	print "I've read", len(returnlist), "stars from", sexcatfile.split("/")[-1]
	return returnlist
	
	
def sortstarlistbyflux(starlist):
	"""starlist is a list of star instances, and we sort it
	according to flux : highest flux first"""
	import operator # for the sorting
	import sys
	sortedstarlist = sorted(starlist, key=operator.itemgetter('flux'))
	sortedstarlist.reverse()
	return sortedstarlist

def sortstarlistby(starlist, measure):
	"""starlist is a list of star instances, and we sort it
	according to the star obejct attribute measure : lowest first"""
	import operator # for the sorting
	import sys
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



def listidentify(selection, biglist, tolerance):
	"""selection is a star list (from a handwritten file) with nice names
	biglist is a big list (e.g. sextractor catalog)
	we return a (sub)list of selection-stars, with nice names but coordinates and fluxes from the biglist"""
	returnlist = []
	if len(biglist) == 0:
		print "The list is empty..."
	elif len(biglist) == 1:
		print "The list is quite small..."
		for handstar in selection:
			closest = handstar.distanceandsort(biglist)
			if closest[0]['dist'] > tolerance:
				print "No match for star", handstar.name
			else:
				newstar = star(closest[0]['star'].x, closest[0]['star'].y, handstar.name, closest[0]['star'].flux , closest[0]['star'].fwhm, closest[0]['star'].ell)
				returnlist.append(newstar)
	else:	
		for handstar in selection:
			closest = handstar.distanceandsort(biglist)
			if closest[0]['dist'] > tolerance:
				print "No match for star", handstar.name
			elif (closest[1]['dist'] - closest[0]['dist']) < tolerance :
				print "Not sure about star", handstar.name
			else:
				newstar = star(closest[0]['star'].x, closest[0]['star'].y, handstar.name, closest[0]['star'].flux , closest[0]['star'].fwhm, closest[0]['star'].ell)
				returnlist.append(newstar)
	return returnlist


def evaluatematch(starlist1, starlist2, tolerance):
	"""Essentially the same as listidentify, but shorter. Starlist1 is the shorter, better list"""
	distances = []
	for star in starlist1:
		dists = star.distanceandsort(starlist2)
		distnearest = dists[0]['dist']
		if distnearest < tolerance:
			distances.append(distnearest)
	return distances
	


def findtrans(autostars, preciserefmanstars, scalingratio, tolerance=2.0, minnbrstars=5.0, mindist=200.0):
	import math
	import sys
	import copy
	"""general fct to find a rotation and shift between two catalogs
	both catalogs should be sorted in flux, and the second one should be smaller for max performance.
	The scalingratio parameter is a float to multiply with a distance of the autostars to match the preciserefmanstars.
	we return a tuple of 3 things :
	- nbr of identified stars (-1 if failed)
	- rotation angle
	- 
	
	"""
	
	# Think of a Hubble expansion with "origin" (0,0)
	# We apply this to the image to align, so that it matches the distances in the reference image.
	autostarscopy = copy.deepcopy(autostars)
	zoomstarlist(autostarscopy, scalingratio)
	
	n = 0 # a counter for the number of tries
	indentlist = []
	for b, brightstar in enumerate(preciserefmanstars[:10]):
		for f, faintstar in enumerate(preciserefmanstars[:10]):
			if f == b: continue
			stardistance = brightstar.distance(faintstar)
			if stardistance < mindist : continue
			
			for bc, brightcandidate in enumerate(autostarscopy[:30]):
				for fc, faintcandidate in enumerate(autostarscopy[:30]):
					if fc == bc: continue
					candidatedistance =  brightcandidate.distance(faintcandidate)
					if math.fabs(candidatedistance - stardistance) > 10: continue
					# we now have a promising pair of pairs, let's check them out.
					n = n+1
					
					starangle = brightstar.trigangle(faintstar)
					candidateangle = brightcandidate.trigangle(faintcandidate)
					rotcandangle = (starangle - candidateangle) % 360.0	# value to "add" to cand to match the star
					
					testcand = copy.deepcopy(brightcandidate)
					testcand.rotate(rotcandangle, (0, 0))
					candshift = testcand.findshift(brightstar)
					
					testcandlist = copy.deepcopy(autostarscopy)
			
					rotatestarlist(testcandlist, rotcandangle, (0, 0))
					shiftstarlist(testcandlist, candshift)
					
					distances = evaluatematch(preciserefmanstars, testcandlist, tolerance)
					indentlist.append(len(distances))
					if len(distances) >= minnbrstars:
						# then we got it !
						
						#print "-"*60
						print "Number of tries :", n
						print "distdiff :", math.fabs(candidatedistance - stardistance)
						print "rotcandangle :", rotcandangle
						#print "candshift :",candshift
						print "Star pairs used :"
						brightstar.write()
						faintstar.write()
						brightcandidate.write()
						faintcandidate.write()
						print "Identified stars :", len(distances), "/", len(preciserefmanstars)
						return (len(distances), rotcandangle, candshift)
					
					#else : try to revert angle !
	
	print "I'm a superhero, but I failed"
	if len(indentlist) > 0:
		print "Maximum identified stars :", max(indentlist)
	return (-1, 0.0, 0.0)				
					
def formpairs(refstars, imgstars, angle, shift, scalingratio, tolerance = 2.0):
	""" we find stars in imgstars that match the refstars if transformed with angle and shift.
	We return a list of star tuples and a comment about how it went.
	"""
	import copy
	transfimgstars = copy.deepcopy(imgstars)
	zoomstarlist(transfimgstars, scalingratio)
	rotatestarlist(transfimgstars, angle, (0, 0))
	shiftstarlist(transfimgstars, shift)
					
	pairs=[]
	nomatch=[]
	notsure=[]
	
	for refstar in refstars:
		closest = refstar.distanceandsort(transfimgstars)
		if closest[0]['dist'] > tolerance:
			print "No match for star", refstar.name
			nomatch.append(refstar.name)
		elif (closest[1]['dist'] - closest[0]['dist']) < tolerance :
			print "Not sure about star", refstar.name
			notsure.append(refstar.name)
		else:
			pairs.append((refstar, imgstars[closest[0]['origpos']]))
	comment = []
	if len(nomatch) > 0 :
		comment.append("No match :")
		for s in nomatch:
			comment.append(" " + s)
		comment.append(" ")
	if len(notsure) > 0 :
		comment.append("Not sure :")
		for s in notsure:
			comment.append(" " + s)
	comment = "".join(comment)
	return (comment, pairs)
	

def writeforgeomap(filename, pairs): 
	import csv
	import sys
	
	table = []	
	for pair in pairs:
		table.append([pair[0].x, pair[0].y, pair[1].x, pair[1].y])

	geomap = open(filename, "wb") # b needed for csv
	writer = csv.writer(geomap, delimiter="\t")
	writer.writerows(table)
	geomap.close()

