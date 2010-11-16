# a first test of the simimg class

execfile("./config.py")

import simimg
from generate_skylist_fcts import *
from variousfct import *
import numpy as np





catalogue=[]



#lets create images with one star, the seeing changing regularly from img to img
seeing_space=np.linspace(0.25,3.5,250)     #minimal seeing, maximal seeing, nb of images

for seeingvalue in seeing_space: 
    thissimimg = simimg.simimg(image_size = (400,400), seeing_fwhm = seeingvalue,  sky_list = skylist_singlestar(x=200,y=200,mag=20))
    catalogue.append(thissimimg)




#we write the catalogue into a pickle
writepickle(catalogue, os.path.join(pipedir, simname + '.pkl'))


