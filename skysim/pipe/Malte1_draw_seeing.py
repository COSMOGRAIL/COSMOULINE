execfile("./config.py")

import skysim_sources
import skysim_images
import variousfct
import numpy as np


sourcelist = variousfct.readpickle("Malte1_sourcelist.pkl")


# We build the images
imagelist = [skysim_images.Simimg((1400, 900), seeing_fwhm = s, sky_list = sourcelist) for s in np.linspace(0.6, 1.8, 10))]

# And write them to files
skysim_images.write_images(imagelist, simname="Malte1_seeing", skypath=sky, workdir=workdir, skyconffile="config.sky")



