#we define some functions to create instances of the class simimg; 

import asciidata
import sys





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


    














    
