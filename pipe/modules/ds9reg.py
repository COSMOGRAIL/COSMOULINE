import os, sys
import numpy as np


"""

A *minimal* class to "parse" DS9 region files.
In fact all it does is to build a mask by reading the "circle" regions.

Malte Tewes, March 2010

"""



class regions:


	def __init__(self, dimx, dimy):
		"""
		Provide dimx and dimy, the dimensions of the mask you want to build.
		In all this class we use plain "physical" pixel coordinates.
		"""
		
		self.dimx = dimx
		self.dimy = dimy
	
		self.circles = []
		self.boxes = []
	
		self.mask = np.cast['bool'](np.zeros((dimx, dimy))) # All False
		
		
	def readds9(self, ds9regfilepath, verbose=True):
		"""
		Reads a ds9 region file and adds its content to self.circles and self.boxes.
		"""
		if verbose:
			print "Reading DS9 region file ..."
		
		if not os.path.isfile(ds9regfilepath):
			print "Error : the DS9 region file"
			print ds9regfilepath
			print "does not exist."
			sys.exit()
		
		ds9regfile = open(ds9regfilepath, "r")
		ds9regfilelines = ds9regfile.readlines()
		ds9regfile.close()
		
		for line in ds9regfilelines:
			if line[0] == "#" or len(line) < 3:
				continue
			if "global" in line:
				continue
			if "physical" in line:
				continue
			if line[0:6] == "circle":
				content = line[7:].strip()
				endi = content.find(")")
				content = content[:endi]
				(x, y, r) = content.split(",")
				self.circles.append({"x":float(x), "y":float(y), "r":float(r)})
			else:
				print "WARNING : unknown region in line : %s" % line.strip()
				continue
			
		
			
	def buildmask(self, verbose = True):
		"""
		Puts the interiors of self.circles to True
		"""
		
		if verbose:
			print "Building region mask ..."
		
		for i in range(self.mask.shape[0]):
			for j in range(self.mask.shape[1]):
				for circle in self.circles:
					squaredist = (i+1 - circle["x"])**2.0 + (j+1 - circle["y"])**2.0
					if (squaredist < circle["r"]**2.0):
						self.mask[i,j] = True
			
		
		
		
		
		
		
		
