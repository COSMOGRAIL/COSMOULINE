#we define some functions to create instances of the class simimg; 

import asciidata
import sys
import random
import math
import cmath





#a simple fct that creates a list containing the position of a star; this list has to be given to skymaker that simulates a star at the given position
def skylist_singlestar(x,y,mag=None):       #if mag is not specified, skymaker will give a random value that depends on certain parameters in the configfile of skymaker
    
    starlist=asciidata.create(3,1)
    starlist[0].rename('Code')
    starlist.header.append('1 Code')
    starlist[1].rename('x')
    starlist.header.append('2 x')
    starlist[2].rename('y')
    starlist.header.append('3 y')


    starlist[0][0]=100                  #code for a stars is 100, for galaxies it would be 200
    starlist[1][0]=x
    starlist[2][0]=y
    
    if mag!=None:
        starlist.append('mag')
        starlist.header.append('4 mag')
        starlist[3][0]=mag
    
    return starlist                    #this is an AsciiData object





##########################################################################################################################################33




#a simple fct that creates a list containing the position of 2 stars; this list has to be given to skymaker that simulates 2 stars at the given positions
def skylist_twostars(x1,y1,x2,y2,mag1=None,mag2=None):       #if mag is not specified, skymaker will give a random value that depends on certain parameters in the configfile of skymaker
    
    starlist=asciidata.create(3,2)
    starlist[0].rename('Code')
    starlist.header.append('1 Code')
    starlist[1].rename('x')
    starlist.header.append('2 x')
    starlist[2].rename('y')
    starlist.header.append('3 y')


    starlist[0][0]=100                  #code for a star
    starlist[1][0]=x1
    starlist[2][0]=y1


    starlist[0][1]=100                  #code for a star
    starlist[1][1]=x2
    starlist[2][1]=y2
    
    if mag1!=None or mag2!=None:
        starlist.append('mag')
        starlist.header.append('4 mag')
        starlist[3][0]=mag1
	starlist[3][1]=mag2


    
  
    return starlist                    #this is an AsciiData object




#######################################################################################################################




#a fct that creates a list containing the position of 5 stars (4 psf and 1 "quasar"); this list has to be given to skymaker that simulates 5 stars at the given position
def skylist_fivestars(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,mag1=None,mag2=None,mag3=None,mag4=None,mag5=None):       #if mag is not specified, skymaker will give a random value that depends on certain parameters
    
    starlist=asciidata.create(3,5)
    starlist[0].rename('Code')
    starlist.header.append('1 Code')
    starlist[1].rename('x')
    starlist.header.append('2 x')
    starlist[2].rename('y')
    starlist.header.append('3 y')

    
    starlist[0][0]=100                  #code for a star
    starlist[1][0]=x1
    starlist[2][0]=y1


    starlist[0][1]=100                  
    starlist[1][1]=x2
    starlist[2][1]=y2

    starlist[0][2]=100                  
    starlist[1][2]=x3
    starlist[2][2]=y3  

    starlist[0][3]=100                  
    starlist[1][3]=x4
    starlist[2][3]=y4

    starlist[0][4]=100                  
    starlist[1][4]=x5
    starlist[2][4]=y5    

    
    starlist.append('mag')
    starlist.header.append('4 mag')
    starlist[3][0]=mag1
    starlist[3][1]=mag2
    starlist[3][2]=mag3
    starlist[3][3]=mag4
    starlist[3][4]=mag5 

  
    return starlist                    #this is an AsciiData object





#######################################################################################################################




#a fct that creates a matrix of stars; you have to specifie the dimensions of the matrix; you may define the distance between neighbouring stars
def skylist_starnetwork(imgdimx, imgdimy, matrix_x, matrix_y, distance=None, mag=None):


    #we create the list
    starlist=asciidata.create(3, matrix_x*matrix_y)
    starlist[0].rename('Code')
    starlist.header.append('1 Code')
    starlist[1].rename('x')
    starlist.header.append('2 x')
    starlist[2].rename('y')
    starlist.header.append('3 y')

    for index in range(starlist.nrows):
        starlist['Code'][index]=100             #code for stars is 100, for galaxies it would be 200

    if mag != None:
        starlist.append('mag')
        starlist.header.append('4 mag')
        for index in range(starlist.nrows):
            starlist['mag'][index]=mag





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
                starlist['x'][j+i*matrix_y] = xborder + (i+1)*dist_x
                starlist['y'][j+i*matrix_y] = yborder + (j+1)*dist_y




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
                starlist['x'][j+i*matrix_y] = start_x + i*distance
                starlist['y'][j+i*matrix_y] = start_y + j*distance




    return starlist                        #an asciidata object



#######################################################################################################################



 #a fct that creates a list of stars with random positions and magnitudes (although skymaker is also able to do that but we want to have the control on it)
  
def skylist_randomstars(imgdimx, imgdimy, nb_stars = 0, mag_min = 17.0, mag_max = 20.0):
	#we create the list
	starlist=asciidata.create(4, nb_stars)
	starlist[0].rename('Code')
	starlist.header.append('1 Code')
	starlist[1].rename('x')
	starlist.header.append('2 x')
	starlist[2].rename('y')
	starlist.header.append('3 y')	
	starlist[3].rename('mag')
	starlist.header.append('4 mag')

    	#we exclude the borders of the image
    	xborder_min=0.1*imgdimx        #no stars on the borders
    	yborder_min=0.1*imgdimy

    	xborder_max=0.9*imgdimx
    	yborder_max=0.9*imgdimy


	for index in range(starlist.nrows):

		starlist['Code'][index]=100	#code for stars is 100, for galaxies it would be 200

		#we set randomly the position of the stars avoiding to put some on the borders of the image
		starlist['x'][index] = random.uniform(xborder_min, xborder_max)
		starlist['y'][index] = random.uniform(yborder_min, yborder_max)

		# we set randomly the magnitude between a max and a min value
		starlist['mag'][index] = random.uniform(mag_min, mag_max) 



	return starlist		#an asciidata object


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



