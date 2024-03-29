"""
Classes and functions about sources to be drawn by Skymaker
"""

import sys, os
import math, cmath, random
import copy


class Star:
	"""
	Stars for a skymaker field
	"""
	
	def __init__(self, pos_x = None, pos_y = None, mag = None, name = None):

		self.code = "100"
		
		if pos_x == None:
			self.pos_x = 10.0
		else:
			self.pos_x = pos_x
			
		if pos_y == None:
			self.pos_y = 10.0
		else:
			self.pos_y = pos_y
				
		if mag == None:
			self.mag = 17.0
		else:
			self.mag = mag
			
		if name == None:
			self.name = "Untitled"
		else:
			self.name = name
		

	def __str__(self) :
		return "%s\t%.3f\t%.3f\t%.3f" % (self.code, self.pos_x, self.pos_y, self.mag)

	def manstr(self) :
		return "%s\t%.2f\t%.2f\t%.3f" % (self.name, self.pos_x, self.pos_y, self.mag)

	def shift(self, shift_x, shift_y):
		self.pos_x += shift_x
		self.pos_y += shift_y


	def rotate(self, angle):
		"""
		The angle is in degrees
		"""
		old_coord=complex(self.pos_x, self.pos_y)
		rotation=cmath.exp(math.radians(angle) * 1j)
		new_coord= rotation * old_coord
		self.pos_x=new_coord.real
		self.pos_y=new_coord.imag


class Galaxy:
	"""
	Galaxies for a skymaker field
	
	# A galaxy at FITS coordinates (102.0,180.7) with "total" magnitude 19.41,
	# bulge-to-total ratio 0.42, bulge equivalent-radius 2.3 arcsec,
	# projected bulge aspect ratio 0.8,
	# bulge position angle 32.3 degrees (CCW, with respect to x axis),
	# disk scale-length 4.0 arcsec, disk inclination (aspect ratio) 0.2, and
	# disk position angle 31.3 degrees (CCW, with respect to x axis),
	200 102.0 180.7 19.41 0.42 2.3 0.8 32.3 4.0 0.2 31.3

	
	"""
	
	def __init__(self, pos_x = None, pos_y = None, mag = None, name = None):

		self.code = "200"
		
		if pos_x == None:
			self.pos_x = 10.0
		else:
			self.pos_x = pos_x
			
		if pos_y == None:
			self.pos_y = 10.0
		else:
			self.pos_y = pos_y
				
		if mag == None:
			self.mag = 17.0
		else:
			self.mag = mag
			
		if name == None:
			self.name = "Untitled"
		else:
			self.name = name
		
		self.bulgratio = 0.3
		self.bulgrad = 2.3 # Bulge radius, arcsec
		self.bulgar = 0.8 # Bulge aspect ratio
		self.bulgpa = 30.0 # Bulge position angle
		self.disksl = 2.0 # Disk scale length, arcsec
		self.diskar = 0.5 # Disk aspect ratio
		self.diskpa = 60.0 # Disk position angle
		

	def __str__(self) :
		return "%s\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f" % (self.code, self.pos_x, self.pos_y, self.mag, self.bulgratio, self.bulgrad, self.bulgar, self.bulgpa, self.disksl, self.diskar, self.diskpa)

	def manstr(self) :
		return "%s\t%.2f\t%.2f" % (self.name, self.pos_x, self.pos_y)

	
	def shift(self, shift_x, shift_y):
		self.pos_x += shift_x
		self.pos_y += shift_y


	def rotate(self, angle):
		"""
		The angle is in degrees
		"""
		old_coord=complex(self.pos_x, self.pos_y)
		rotation=cmath.exp(math.radians(angle) * 1j)
		new_coord= rotation * old_coord
		self.pos_x=new_coord.real
		self.pos_y=new_coord.imag




def write_sourcelist(filepath, sourcelist):
	"""
	Writes a skymaker input file from a list of sources
	"""
	outfile = open(filepath, 'w')
	outfile.write("\n".join([str(s) for s in sourcelist]))
	outfile.close()

def write_mancat(filepath, sourcelist):
	"""
	Writes a "mancat" (manual catalog) from a list of sources
	Format :
	sourcename	x	y	flux
	"""
	outfile = open(filepath, 'w')
	outfile.write("\n".join([s.manstr() for s in sourcelist]))
	outfile.close()




def build_array_stars(image_size, matrix_x, matrix_y, distance=None, mag=None):
	"""
	a fct that creates a matrix of stars; you have to specifie the dimensions of the matrix; you may define the distance between neighbouring stars
	"""

	#we create the list
	starlist = []


	#we exclude the borders of the image
	xborder=0.1*image_size[0]        #no stars on the borders
	yborder=0.1*image_size[1]
	effective_x=image_size[0]  - 2.0*xborder
	effective_y=image_size[1]  - 2.0*yborder




	################ case with unspecified distance   ###############
	if distance==None:

		dist_x=effective_x / float(matrix_x + 1)
		dist_y=effective_y / float(matrix_y + 1)


		# we iterate in the following way over the matrix (example with matrix_x=3, matrix_y=2):
		#1 3 5
		#0 2 4

		for i in range(matrix_x):
			for j in range(matrix_y):
				x = xborder + (i+1)*dist_x
				y = yborder + (j+1)*dist_y
				starlist.append(Star(pos_x = x, pos_y = y, mag = mag))



	############### case with specified distance   #################
	else:
		if (matrix_x-1)*distance > effective_x or (matrix_y-1)*distance > effective_y:
			print('Problem while creating starnetwork list:')
			print('distance between stars to big to put specified nb of stars into the image')
			sys.exit()


		start_x = xborder + (effective_x - (matrix_x-1)*distance)/2.0       #where to put the first star in x direction
		start_y = yborder + (effective_y - (matrix_y-1)*distance)/2.0       #where to put the first star in y direction

		for i in range(matrix_x):
			for j in range(matrix_y):
				x = start_x + i*distance
				y = start_y + j*distance
				starlist.append(Star(pos_x = x, pos_y = y, mag = mag))



	return starlist   #a list of instances of the class star


  
def build_random_stars(image_size, nb_stars = 0, mag_min = 17.0, mag_max = 20.0, min_dist=None):
	"""
	a fct that creates a list of stars with random positions and magnitudes
	you can specify a minimal distance between the stars, the avoid stars too close to each other

	"""

	starlist = []

	#we exclude the borders of the image;no stars on the borders 
	xborder_min=0.1*image_size[0]
	yborder_min=0.1*image_size[1]

	xborder_max=0.9*image_size[0]
	yborder_max=0.9*image_size[1]


	##############################   case with no minimal distance    #########################
	if min_dist == None:
		for i in range(nb_stars):
			#we set randomly the position of the stars avoiding to put some on the borders of the image; we also generate the mag
			x = random.uniform(xborder_min, xborder_max)
			y = random.uniform(yborder_min, yborder_max)
			mag = random.uniform(mag_min, mag_max)
			starlist.append(Star(pos_x = x, pos_y = y, mag = mag))


	#################################  case with specified minimal distance    ##############
	else:
		while len(starlist) < nb_stars:
			x = random.uniform(xborder_min, xborder_max)
			y = random.uniform(yborder_min, yborder_max)
			mag = random.uniform(mag_min, mag_max)
			thisstar=Star(pos_x = x, pos_y = y, mag = mag )
			#starlist.append(thisstar)
		
			#now we test if the generated coords do not violate the minimal distance condition
			too_close=False

			for star in starlist:
				if ((star.pos_x-thisstar.pos_x)**2.0 + (star.pos_y-thisstar.pos_y)**2.0)**(0.5) < min_dist:
					too_close = True
					break

			if not too_close:
				starlist.append(thisstar)


	return starlist		


def jitter_sourcelist(inputlist, allthesame=False):
	"""
	Add a uniform shit in [0, 1] pixel X and Y to the sources in inputlist,
	either one random shift for each source, or one same shift for all sources.
	This is made to avoid having PSF stars always on the same pixels etc.
	"""
	
	outputlist = copy.deepcopy(inputlist)
	
	if allthesame:
		shiftx = random.uniform(0.0, 1.0)
		shifty = random.uniform(0.0, 1.0)
		for s in outputlist:
			s.shift(shiftx, shifty)

	else:
		for s in outputlist:
			shiftx = random.uniform(0.0, 1.0)
			shifty = random.uniform(0.0, 1.0)
			s.shift(shiftx, shifty)
	return outputlist
	


def shiftrot_sourcelist(inputlist, shiftx=0, shifty=0, angle=0):
	"""
	a fct that takes an input list and return a list with all the stars shifted and rotated. Notice that we first apply the shift and then the rotation!
	the angle is in degrees, the shift in pixels
	"""
	#we create a deep copy of the input starlist:
	outputlist = copy.deepcopy(inputlist)

	#we apply the transformation
	for s in outputlist:
		s.shift(shiftx, shifty)
		s.rotate(angle)

	return outputlist



def random_shiftrot_sourcelist(inputlist, shiftx_max=0, shifty_max=0, angle_max=0):
	"""
	a fct that applies a random shift and a random rotation to a starlist, where the shift is contained in [-shift_max, shift_max] and the angle is contained in [-angle_max, angle_max]
	Units: shift [pixel], angle [degrees]
	"""

	print('I will apply a coordinate transformation with the following properties:')
	print('Shift in x direction between %.2f and %.2f pixels.' %(-abs(shiftx_max), abs(shiftx_max)))
	print('Shift in y direction between %.2f and %.2f pixels.' %(-abs(shifty_max), abs(shifty_max)))
	print('Rotation between %.4f and %.4f degrees.' %(-abs(angle_max), abs(angle_max)))   

	shiftx = random.uniform( - shiftx_max, shiftx_max)     #no problem if -shiftx_max > shiftx_max
	shifty = random.uniform( - shifty_max, shifty_max)
	angle = random.uniform( - angle_max, angle_max)

	return shiftrot_sourcelist(inputlist, shiftx, shifty, angle)

