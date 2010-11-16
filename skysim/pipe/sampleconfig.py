#Configuration file for the generation of simulated images
import sys
import os

#default parameters

gain = 1.0
detector_effic = 1.0	#quantum efficiency of the detector
exptime = 300.0
pixel_size = 0.2	#in arcsecond
telescope_diam = 3.6

sky_level = 1000.0	#sky level in ADU

back_mag = -2.5*np.log10((4.0 *sky_level * gain * detector_effic)/(exptime * np.pi * telescope_diam**2)) / pixel_size**2	# background surface brightness (mag/arsec2)


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
