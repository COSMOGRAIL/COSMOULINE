#definition of a class of star to be used to create a list of star for skymaker

class Star:

	def __init__(self, pos_x = None, pos_y = None, star_mag = None):
		
		self.code = 100
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.mag = star_mag
		


	def __str__(self) :
		return "%i\t%.3f\t%.3f\t%.3f" % (self.code, self.pos_x, self.pos_y, self.mag)



#myfile.write("\n".join([str(s) for s in catalog])

