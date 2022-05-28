import math
import sys
import os
import shutil
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from modules import variousfct
from config import settings, pklfilepath

deconvname = settings['deconvname']
toaddsourcenames = settings['toaddsourcenames']
sumsourcename = settings['sumsourcename']

if len(toaddsourcenames) == 0:
    print("Nothing to sum: your `toaddsourcenames` in your `settings.py` file")
    print("is empty. Exiting.")
    sys.exit()


toaddfluxfields = [f"out_{deconvname}_{sourcename}_flux" 
                                       for sourcename in toaddsourcenames]
toaddshotnoisefields = [f"out_{deconvname}_{sourcename}_shotnoise" 
                                       for sourcename in toaddsourcenames]

sumfluxfield = f"out_{deconvname}_{sumsourcename}_flux"
sumshotnoisefield = f"out_{deconvname}_{sumsourcename}_shotnoise"


addcode = sumsourcename  + "=" + "+".join(toaddsourcenames)
print(f"Operation : {addcode}")

filenameels = os.path.splitext(pklfilepath)
newdbfilepath = filenameels[0] + "_" + addcode + filenameels[1]

if os.path.exists(newdbfilepath):
	raise RuntimeError("Output file exists, please remove it !")

shutil.copy(pklfilepath, newdbfilepath)

images = variousfct.readpickle(newdbfilepath, verbose=True)
print(f"{len(images)} images in db.")

for image in images:
	image[sumfluxfield] = None
	image[sumshotnoisefield] = None
	
	fluxes = [image[fieldname] for fieldname in toaddfluxfields]
	shotnoises = [image[fieldname] for fieldname in toaddshotnoisefields]
	if not (None in fluxes) :
		# We sum the fluxes, and take the geometric sum of the shotnoises
        # (very plausible).
		image[sumfluxfield] = sum(fluxes)
		image[sumshotnoisefield] = math.sqrt(float(sum([s*s for s in shotnoises])))


variousfct.writepickle(images, newdbfilepath, verbose=True)
print("Ok done, this is the new dbfilename to use :")
print(os.path.basename(newdbfilepath))
