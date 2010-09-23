
def getangle(filename):		# fetches the keywork ROTSKYPA from the header of a fits file
	import pyfits
	fits = pyfits.open(filename)
	#angle = float(fits[0].header['ROTANGLE'])
	angle = float(fits[0].header['ROTSKYPA'])
	return angle


def getcenter(filename):	# fetches the center of rotation from the header of a fits file
	import pyfits
	fits = pyfits.open(filename)
	#angle = float(fits[0].header['ROTANGLE'])
	x = float(fits[0].header['ROTCENTX'])
	y = float(fits[0].header['ROTCENTY'])
	return [x,y]


def getnbrightstars(sexcat, n):		# reads a sextractor catalog and returns the coordinates of the brightest stars
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
		flux = float(elements[1])
		xpos = float(elements[3])
		ypos = float(elements[4])
		ell = float(elements[9])
		flag = int(elements[10])
		fwhm = float(elements[11])
		#print ell, flag, fwhm
		if flag == 0 and fwhm > 0.01:
			table.append([xpos, ypos, flux])
	
	sortedtable = sorted(table, key=operator.itemgetter(2)) # sort stars according to flux
	sortedtable.reverse()
	selection = sortedtable[:n]
	for star in selection:
		del star[2]
	return selection

def getmanstars(mancat):	# reads a simple coordinate file with "x y" on each line
 	import sys
	
	cat = open(mancat, 'r')
	catlines = cat.readlines()
	cat.close()
	table = []
	for catline in catlines:
		if catline[0] == '#' or len(catline) < 4:
			continue
		elements = catline.split()
		if len(elements) != 2:
			print "Wrong format :", mancat
			sys.exit()
		xpos = float(elements[0])
		ypos = float(elements[1])
		table.append([xpos, ypos])
	
	print "I've read", len(table), "stars from a hand-written file."
	return table
	
	
def rotatecoords(coordlist, degrees, center):	# does a matrix like rotation but without matrixes...
	import math
	rotcoordlist = []
	anglerad = math.pi*degrees/180.0
	rota = 	math.cos(anglerad)
	rotb = -math.sin(anglerad)
	rotc = -rotb
	rotd = rota
	
	for star in coordlist:
		xs = star[0] - center[0]
		ys = star[1] - center[1]
		us = rota*xs + rotb*ys
		vs = rotc*xs + rotd*ys
		u = us + center[0]
		v = vs + center[1]
		rotcoordlist.append([u,v])
		
	return rotcoordlist

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


def doshift(stars, shift):	# returns stars + shift
	# shiftedstars = stars[:]  # this is not enough, as each element is mutable !
	shiftedstars=[]
	for star in stars:
		shiftedstars.append([star[0] + shift[0],star[1] + shift[1]])
	return shiftedstars


def findclosest(point, starlist):		# returns the position of the closest star in starlist, and the corresponding distance
	import operator # for the sorting
	import sys
	mindist = 10000.0
	pos = 0
	nextdist = 10000.0
	nextpos = 0
	#for i, star in enumerate(starlist):
	#	dist = distance(point, star)
	#	if dist < mindist:
	#		mindist = dist
	#		pos = i
	
	distances=[]
	for i, star in enumerate(starlist):
		dist = distance(point, star)
		distances.append([i, dist])
	
	sorteddistances = sorted(distances, key=operator.itemgetter(1)) # sort stars according to dist
	
	if len(starlist) > 1 :
		mindist = sorteddistances[0][1]
		pos = sorteddistances[0][0]
		nextdist = sorteddistances[1][1]
		nextpos = sorteddistances[1][0]
	else:
		print "findclosest with to short list !"
		sys.exit()
		
	return pos, mindist, nextpos, nextdist


def identify(listone, listtwo, maxdist):
	posone=[] # the positions in listone of the found stars
	postwo=[] # the positions in listtwo of the corresponding stars
	starsone=[] # the actual star coordinates
	starstwo=[]
	nbrnotfound = 0 # refers to the stars in listone, which should be the shorter "reference list"
	
	for i, one in enumerate(listone):
		pos, dist, nextpos, nextdist = findclosest(one, listtwo)
		if dist > maxdist:
			nbrnotfound = nbrnotfound + 1
			print "No match for star", i+1
		elif (nextdist - dist) < maxdist :
			nbrnotfound = nbrnotfound + 1
			print "Not sure about star", i+1
		else:
			posone.append(i)
			starsone.append(one)
			postwo.append(pos)
			starstwo.append(listtwo[pos])
		
	return nbrnotfound, posone, postwo, starsone, starstwo
	
def median(floats):
	
	lenf = len(floats)
	sortedfloats = sorted(floats)
	if lenf == 0:
		return 0.0
	if lenf & 1:
		return sortedfloats[lenf // 2]
	else:
		return 0.5*(sortedfloats[lenf // 2 - 1] + sortedfloats[lenf // 2])
	

def evaluatematch(stars1, stars2, tolerance):	# quantifies the match between two catalogus of coordinates
	
	distances = []
	for star in stars1:
		pos, dist, nextpos, nextdist = findclosest(star, stars2)
		if dist < tolerance:
			distances.append(dist)
	
	return median(distances), len(distances)
	

	
def catshift(refstars, stars, nb, tolerance): # tries to estimate a (x, y) shift between two ("non-corresponding") lists of stars
	
	# it helps a lot if refstars and stars are sorted according to brightness
	#
	# returns a shift if nb+ stars within tolerance
	# call this function with a very high nb, and it will always return the highest number of identifications.
	
	bestnident = -1
	for i,refstar in enumerate(refstars):
		#print "Ref    : %2d (%7.2f, %7.2f)" % (i+1, refstar[0], refstar[1])
		for j,star in enumerate(stars):
			shift = shiftbetweenstars(refstar, star)
			shiftedstars = doshift(stars, shift)
			meddist, nident = evaluatematch(refstars, shiftedstars, tolerance)
			#print "  Star : %2d (%7.2f, %7.2f) -> %2d %6.2f " % (j+1, star[0], star[1], nident, meddist)
			if (nident >= nb and meddist < tolerance) :
				print "Got it !", nident, meddist
				return shift
			
			if nident > bestnident:
				bestnident = nident
		if i == 5:
			break
			
	#print "=== Identification failed ! ==="
	return bestnident



def exploreangle(stars, angleini, anglefin, anglestep, center, refstars, nbmin, tolerance):
	# if the provided rotator position does not work, let's turn this a bit !
	# to do so, we will call catshift with high nb value, to find optimal angle.
	# once the best angle found, we just call catshift and return "shift"
	
	nbsteps = int(round((anglefin-angleini)/anglestep))
	
	angles = []
	nidents = []
	
	for i in range(nbsteps):
		angle = angleini + i*anglestep
		angles.append(angle)
		rotstars = rotatecoords(stars, angle, center)	
		nident = catshift(refstars, rotstars, 1000, tolerance)
		nidents.append(nident)
		print nident, angle
	
	maxnident = -1
	maxi = -1
	for i in range(nbsteps):
		if nidents[i] > maxnident:
			maxnident = nidents[i]
			maxi = i
	
	actualangle = angles[maxi] 
	print "maxnident :", maxnident, "  angle :", actualangle
	
	rotstars = rotatecoords(stars, actualangle, center)	
	shift = catshift(refstars, rotstars, nbmin, tolerance)
		
	return actualangle, shift

def writeforgeomap(filename, refstars, posone, stars, postwo): 
	#
	# refstars : posone gives which ones to write
	# stars : postwo gives which ones to write
	#
	import csv
	import sys
	
	if len(posone) != len(postwo):
		print "Error GHR-345_c : GAME OVER"
		sys.exit()	

	table = []	
	for i, one in enumerate(posone):
		star = stars[postwo[i]]
		refstar = refstars[one]
		table.append([refstar[0], refstar[1], star[0], star[1]])

	geomap = open(filename, "wb")
	writer = csv.writer(geomap, delimiter="\t")
	writer.writerows(table)
	geomap.close()

