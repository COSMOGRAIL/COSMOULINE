#
# some fct for the calccoeff script
#
from numpy import *
from star import *

# these fcts are replaced by the star class !
"""
def getnormstars(mancat):	# reads a simple star coordinate file with "starid x y" on each uncommented line and returns a table
 	import sys
	
	cat = open(mancat, 'r')
	catlines = cat.readlines()
	cat.close()
	table = []
	for catline in catlines:
		if catline[0] == '#' or len(catline) < 4:
			continue
		elements = catline.split()
		if len(elements) != 3:
			print "Wrong format :", mancat
			sys.exit()
		starid = int(elements[0])
		xpos = float(elements[1])
		ypos = float(elements[2])
		table.append([starid, xpos, ypos])
	
	print "I've read", len(table), "stars from a hand-written file."
	return table

def getsexstars(sexcat):		# reads a sextractor catalog and returns the coordinates of the good stars
 	import operator # for the sorting
	import sys
	
	cat = open(sexcat, 'r')
	catlines = cat.readlines()
	cat.close()
	
	table = []
	
	for catline in catlines:
		if catline[0] == "#":
			continue
		elements = catline.split()
		if len(elements) != 12:
			print "Wrong sextractor catalog format in", sexcat
			sys.exit()
		flux_aper = float(elements[1])
		fluxerr_aper = float(elements[2])
		xpos = float(elements[3])
		ypos = float(elements[4])
		ell = float(elements[9])
		flag = int(elements[10])
		fwhm = float(elements[11])
		#print ell, flag, fwhm
		if flag == 0 and fwhm > 0.01:
			table.append([xpos, ypos, flux_aper, fluxerr_aper])
	
	sortedtable = sorted(table, key=operator.itemgetter(2)) # sort stars according to flux
	sortedtable.reverse() # so that the brightest come first
	return sortedtable


def shiftbetweenstars(star1, star2): # returns 1 - 2
	shift = [0,0]
	shift[0] = star1[0] - star2[0]
	shift[1] = star1[1] - star2[1]
	return shift

def distance(star1, star2):
	import math
	shift = shiftbetweenstars(star1, star2)
	distance = math.sqrt(shift[0]*shift[0] + shift[1]*shift[1])
	return distance

def findclosest(normstar, catstars):		# returns the position of the 2 closest stars in starlist
	import operator # for the sorting
	import sys
	mindist = 10000.0
	pos = 0
	nextmindist = 10000.0
	nextpos = 0
	
	distances=[]
	for i, star in enumerate(catstars):
		dist = distance(normstar[1:], star[:2])
		distances.append([i, dist])
	
	sorteddistances = sorted(distances, key=operator.itemgetter(1)) # sort stars according to dist
	
	if len(catstars) > 1 :
		mindist = sorteddistances[0][1]
		pos = sorteddistances[0][0]
		nextmindist = sorteddistances[1][1]
		nextpos = sorteddistances[1][0]
	else:
		print "findclosest with to short list !"
		sys.exit()		
	return pos, mindist, nextpos, nextmindist


def identify(normstars, catstars, maxdist):

	identstars=[]
	
	for normstar in normstars:
		pos, mindist, nextpos, nextmindist = findclosest(normstar, catstars)
		if mindist > maxdist :
			print "Normstar", normstar[0], ": no match (", mindist, ")"
		elif (nextmindist - mindist) < maxdist :
			print "Normstar", normstar[0], ": not sure, skipped (", mindist, nextmindist, ")"
		else:
			print "Normstar", normstar[0], ": distance", mindist
			identstars.append([normstar[0], catstars[pos][0], catstars[pos][1], catstars[pos][2], catstars[pos][3]])
			#	starid, x, y, flux_aper, fluxerr_aper
	return identstars
"""

# nice but now we use numpy
"""
def median(floats):
	lenf = len(floats)
	sortedfloats = sorted(floats)
	if lenf == 0:
		return 0.0
	if lenf & 1:
		return sortedfloats[lenf // 2]
	else:
		return 0.5*(sortedfloats[lenf // 2 - 1] + sortedfloats[lenf // 2])	
"""

def simplemediancoeff(refidentstars, identstars):
	#
	# calculates a simple (but try to get that better ... it's pretty good !) multiplicative coeff for each image
	# "calc one coef for each star and take the median of them"
	# coef = reference / image
	
	
	coeffs = []
	for refstar in refidentstars:
		for star in identstars:
			if refstar.name != star.name:
				continue
			coeffs.append(refstar.flux/star.flux)
			break
			
	if len(coeffs) > 0:
		coeffarr = array(coeffs)
		stddev = coeffarr.std()
		return len(coeffs), float(median(coeffs)), float(stddev), float(max(coeffs) - min(coeffs))
	else:	
		return 0, 1.0, 99.0, 99.0
	
	
	
	
	
	
	
