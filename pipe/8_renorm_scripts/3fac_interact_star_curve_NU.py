"""
Now that the coeffs are in the db, you might want to plot curves
(very similar to those made by the renormalize script), but for other stars,
not involved in the renormalization.
"""

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings
from modules.kirbybase import KirbyBase

renormname = settings['renormname']
workdir = settings['workdir']


print("I will plot lightcurves using renormalization coefficient called :")
print(renormname)

print("I take command line arguments, example usage :")
print("python 3_interact_star_curve.py dec_full_e_medcoeff_pyMCSabcdefg3 e")

deckey = sys.argv[1]
sourcename = sys.argv[2]


db = KirbyBase(imgdb)
allimages = db.select(imgdb, ['gogogo', 'treatme'], 
                             [True, True], 
                             returnType='dict', 
                             sortFields=['mjd'])
print(f"{len(allimages)} images in total.")




deckeyfilenumfield = "decfilenum_" + deckey
fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
errorfieldname = "out_" + deckey + "_" + sourcename + "_shotnoise"
decnormfieldname = "decnorm_" + deckey
	
images = [image for image in allimages if image[deckeyfilenumfield] != None]
print(f"{len(images)} images")

fluxes = np.array([image[fluxfieldname] for image in images])
errors = np.array([image[errorfieldname] for image in images])
decnormcoeffs = np.array([image[decnormfieldname] for image in images])
airmasses = np.array([image["airmass"] for image in images])
skylevels = np.array([image["skylevel"] for image in images])

renormcoeffs = np.array([image[renormname] for image in images])
	
renormfluxes = fluxes*renormcoeffs
renormerrors = errors*renormcoeffs
ref = np.median(renormfluxes)
	
mhjds = np.array([image["mhjd"] for image in images])
	
plt.figure(figsize=(15,10))

plt.errorbar(mhjds, renormfluxes/ref, yerr=renormerrors/ref, 
                                      ecolor=(0.8, 0.8, 0.8), 
                                      linestyle="None", 
                                      marker=".")
	

plt.title(f"Source {sourcename}, {deckey}, normalized with {renormname}")
plt.xlabel("MHJD")
plt.ylabel("Flux in electrons / median")
plt.grid(True)
#plt.ylim(0.95, 1.05)
plt.ylim(0.90, 1.1)
plt.xlim(np.min(mhjds), np.max(mhjds))
	

plt.show()
