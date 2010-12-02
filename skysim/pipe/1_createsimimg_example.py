# a first test of the simimg class

execfile("./config.py")

import simimg
from generate_skylist_fcts import *
from variousfct import *
import numpy as np
from star import *

print 'Hello skywalker! So you want to create instances of the simimg class called %s, is this true?' %(simname)
proquest(askquestions)



list_stars=[]


# first we create a single star using the class Star and we add it to the catalog (you can add as much as you want)
list_stars.append(Star(pos_x = 300.0, pos_y = 300.0, star_mag = 19.0))


# then we create several images with the previous star and with a varying seeing

catalogue = []

for seeing in np.linspace(0.45,3.0,1):	

	thissimimg = simimg.simimg(image_size = (600,600), seeing_fwhm = seeing, sky_list = list_stars)

	catalogue.append(thissimimg)	#we add the image in the catalog of image we want to create.




#we write the catalogue into a pickle
writepickle(catalogue, os.path.join(workdir, simname + '.pkl'))



