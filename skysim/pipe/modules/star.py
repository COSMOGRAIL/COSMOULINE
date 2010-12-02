#definition of a class of star to be used to create a list of star for skymaker
import math
import cmath


class Star:

    def __init__(self, pos_x = None, pos_y = None, mag = None):
		
        self.code = 100
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.mag = mag
		

    def __str__(self) :
        return "%i\t%.3f\t%.3f\t%.3f" % (self.code, self.pos_x, self.pos_y, self.mag)


    def shift(self, shift_x, shift_y)
        self.pos_x += shift_x
        self.pos_y += shift_y


    def rotate(self, angle)           #the angle is in degrees
        old_coord=complex(self.pos_x, self.pos_y)
        rotation=cmath.exp(math.radians(angle) * 1j)
        new_coord= rotation * old_coord
        self.pos_x=new_coord.real
        self.pos_y=new_coord.imag


#myfile.write("\n".join([str(s) for s in catalog])

