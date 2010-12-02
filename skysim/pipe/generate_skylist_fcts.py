#we define some functions that are useful to create instances of the class simimg in another script; 

import sys
import random
import copy
from star import *


# a simple function to write an ascii file from a list of stars
def writeto(filepath, list_stars):
	import sys
	import os

	outfile = open(filepath, 'w')
	outfile.write("\n".join([str(star) for star in list_stars]))
	outfile.close()



#######################################################################################################################




#a fct that creates a matrix of stars; you have to specifie the dimensions of the matrix; you may define the distance between neighbouring stars
def skylist_starnetwork(imgdimx, imgdimy, matrix_x, matrix_y, distance=None, mag=None):


    #we create the list
    starlist = []


    #we exclude the borders of the image
    xborder=0.1*imgdimx        #no stars on the borders
    yborder=0.1*imgdimy
    effective_x=imgdimx - 2.0*xborder
    effective_y=imgdimy - 2.0*yborder




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
            print 'Problem while creating starnetwork list:'
            print 'distance between stars to big to put specified nb of stars into the image'
            sys.exit()

        
        start_x = xborder + (effective_x - (matrix_x-1)*distance)/2.0       #where to put the first star in x direction
        start_y = yborder + (effective_y - (matrix_y-1)*distance)/2.0       #where to put the first star in y direction

        for i in range(matrix_x):
            for j in range(matrix_y):
                x = start_x + i*distance
                y = start_y + j*distance
		starlist.append(Star(pos_x = x, pos_y = y, mag = mag))



    return starlist                        #a list of instances of the class star



#######################################################################################################################



 #a fct that creates a list of stars with random positions and magnitudes (although skymaker is also able to do that but we want to have the control on it)
  
def skylist_randomstars(imgdimx, imgdimy, nb_stars = 0, mag_min = 17.0, mag_max = 20.0):
	#we create the list
	starlist = []

    	#we exclude the borders of the image
    	xborder_min=0.1*imgdimx        #no stars on the borders
    	yborder_min=0.1*imgdimy

    	xborder_max=0.9*imgdimx
    	yborder_max=0.9*imgdimy


	for index in range(nb_stars):

		#we set randomly the position of the stars avoiding to put some on the borders of the image
		x = random.uniform(xborder_min, xborder_max)
		y = random.uniform(yborder_min, yborder_max)

		# we set randomly the magnitude between a max and a min value
		mag = random.uniform(mag_min, mag_max) 

		starlist.append(Star(pos_x = x, pos_y = y, mag = mag))

	return starlist		




#####################################################################################################################
#a fct that takes an input list and return a list with all the stars shifted and rotated
#the angle is in degrees, the shift in pixels

def rot_shift_starlist(inputlist, shiftx, shifty, angle):

    #we create a deep copy of the input starlist:
    outputlist = copy.deepcopy(inputlist)
    

    #we apply the transformation
    for Star in outputlist:
        Star.shift(shiftx, shifty)
        Star.rotate(angle)

    return outputlist






######################################################################################################################
#a fct that applies a random shift/rotation to a starlist, where the shift is contained in [-shift_max, shift_max] and the angle is contained in [-angle_max, angle_max]
#Units: shift [pixel], angle [degrees]

def random_rot_shift_starlist(inputlist, shiftx_max, shifty_max, angle_max):
    print 'I will apply a coordinate transformation with the following properties:'
    print 'Shift in x direction between %.2f and %.2f pixels.' %(-abs(shiftx_max), abs(shiftx_max))
    print 'Shift in y direction between %.2f and %.2f pixels.' %(-abs(shifty_max), abs(shifty_max))
    print 'Rotation between %.4f and %.4f degrees.' %(-abs(angle_max), abs(angle_max))   

    shiftx = random.uniform( - shiftx_max, shiftx_max)     #no problem if -shiftx_max > shiftx_max
    shifty = random.uniform( - shifty_max, shifty_max)
    angle = random.uniform( - angle_max, angle_max)

    return rot_shift_starlist(inputlist, shiftx, shifty, angle)









