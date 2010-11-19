# a first test of the simimg class

execfile("./config.py")

import simimg
from generate_skylist_fcts import *
from variousfct import *
import numpy as np


print 'Hello skywalker! So you want to create instances of the simimg class called %s, is this true?' %(simname)
proquest(askquestions)



catalogue=[]



#lets create images with one star, the seeing changing regularly from img to img
seeing_space=np.linspace(0.45,3.7,250)     #minimal seeing, maximal seeing, nb of images

for seeingvalue in seeing_space: 
    thissimimg = simimg.simimg(image_size = (400,400), seeing_fwhm = seeingvalue,  sky_list = skylist_singlestar(x=200,y=200,mag=20))
    catalogue.append(thissimimg)




#we write the catalogue into a pickle
writepickle(catalogue, os.path.join(pipedir, simname + '.pkl'))



