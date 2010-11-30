#Configuration file for the generation of simulated images
import sys
import os
import numpy as np


#the path of the skymaker software
sky = '/home/epfl/tewes/bin/skymaker-3.3.3/src/sky'


#give a name for the set of simulated images (for ex. sim_seeing)
simname='test_seeing'


#where are the scripts (including this config.py) 
pipedir='/home/epfl/cataldi/skysim/pipe_svn'

# to get access to all our modules without installing anything :
sys.path.append(os.path.join(pipedir, "modules"))

#where to put the produced images
workdir="/home/epfl/cataldi/unsaved/skysim_work"



#switches
askquestions=True
