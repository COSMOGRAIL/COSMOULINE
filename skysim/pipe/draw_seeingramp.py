execfile("./config.py")

import skysim_sources
import skysim_images
import numpy as np

sourcelist = variousfct.readpickle("sourcelist_default.pkl")

# We draw 20 images, with different values for the seeing FWHM.
imagelist = []
for s in np.linspace(0.6, 1.8, 50) :
	# For each image, we add a random shift (uniform 0 -> 1 pixel) to all the sources (same shift for all sources).
	# This is to "sample" different samplings...
	jitteredsourcelist = skysim_sources.jitter_sourcelist(sourcelist, allthesame = True)
	img = skysim_images.Simimg(image_size=(1400, 900), sky_list = jitteredsourcelist, seeing_fwhm = s, image_name = "seeing%.2f" % (s))
	imagelist.append(img)


# And write them to files
skysim_images.write_images(imagelist, simname="seeingramp", skypath=sky, workdir=workdir, skyconffile="config.sky", makepngs=True, pngrebin=1)



