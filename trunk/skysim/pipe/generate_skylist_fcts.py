#we define some functions that are useful to create instances of the class simimg in another script; 

import sys
import random
import math
import cmath
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


        #fill in the list



        # we iterate in the following way over the matrix (example with matrix_x=3, matrix_y=2):
        #1 3 5
        #0 2 4

        for i in range(matrix_x):
            for j in range(matrix_y):
                x = xborder + (i+1)*dist_x
                y = yborder + (j+1)*dist_y
		starlist.append(Star(pos_x = x, pos_y = y, star_mag = mag))



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
		starlist.append(Star(pos_x = x, pos_y = y, star_mag = mag))



    return starlist                        #a list python



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

		starlist.append(Star(pos_x = x, pos_y = y, star_mag = mag))

	return starlist		#a list python


#####################################################################################################################
#a fct that rotates and applies a shift to a starlist
#the angle is in degrees, the shift in pixels

def rot_shift_starlist(inputlist, shiftx, shifty, angle):

    #we create a deep copy of the input starlist:
    outputlist=asciidata.create(len(inputlist), inputlist.nrows)
    for index in range(len(inputlist)):
        outputlist[index] = inputlist[index].copy()


    #we use complex numbers to generate to coord transformation
    shift = complex(shiftx, shifty)
    rotation = cmath.exp(math.radians(angle)*1j)
    

    #we apply the transformation
    for index in range(outputlist.nrows):
        inputcoords =  complex(outputlist['x'][index], outputlist['y'][index])
        outputcoords = rotation * inputcoords + shift                           #the transformed coords in complex notation
        outputlist['x'][index] = outputcoords.real
        outputlist['y'][index] = outputcoords.imag


    return outputlist



######################################################################################################################

#a fct that takes a starlist (asciidata object) as input and returns a couple of new starlists rotated and shifted with respect to the input starlist
#the fct will simply modify the coordinates of the stars in the input starlist
#nb_starlist is the number of starlists you want to create
#shift_max is in pixels, angle_max in degrees; they give the maximal value of the absolute value of the random shift/angle we apply to the input starlist
#(i.e. if angle_max=10, there will be rotations between -10 and 10 degrees)


def generate_rot_shift_starlists(inputlist, nb_starlists, shiftx_max, shifty_max, angle_max):

    print 'I will apply coordinate transformations with the following properties:'
    print 'Shift in x direction between %.2f and %.2f pixels.' %(-abs(shiftx_max), abs(shiftx_max))
    print 'Shift in y direction between %.2f and %.2f pixels.' %(-abs(shifty_max), abs(shifty_max))
    print 'Rotation between %.4f and %.4f degrees.' %(-abs(angle_max), abs(angle_max))


    starlists=[]



    #Now we create the starlists
    for i in range(nb_starlists):
        print 'Generating transformed starlist ', i+1, "/", nb_starlists


        #we calculat the shift and the rotation angle for the starlist to generate

        shiftx = random.uniform( - shiftx_max, shiftx_max)     #no problem if -shiftx_max > shiftx_max
        shifty = random.uniform( - shifty_max, shifty_max)
        angle = random.uniform( - angle_max, angle_max)
        

        transf_list = rot_shift_starlist(inputlist, shiftx, shifty, angle)


        starlists.append(transf_list)


    return starlists                                    #a list of asciidata objects




