#
# Simply plot lightcurves using the Sextractor aperture photometry of objects.
#
#
#


execfile("../config.py")
#from kirbybase import KirbyBase, KBError
#from calccoeff_fct import *
from variousfct import *
#from star import *
import matplotlib.pyplot as plt
import numpy as np


lcdict = readpickle(os.path.join(plotdir, "sexfluxdb.pkl"))


magarrays = []
azarrays = []
colorarrays = []
mjdarrays = []
labels = []

for starname in sorted(lcdict.keys()):
	mjdarray = np.array(lcdict[starname]["mjds"])
	fluxarray = np.array(lcdict[starname]["fluxes"]) * np.array(lcdict[starname]["medcoeffs"])
	
	magarray = -2.5 * np.log10(fluxarray)
	#plt.plot(mjdarray, magarray, ".", label = starname)
	
	seeingarray = np.array(lcdict[starname]["seeings"])
	fwhmarray = np.array(lcdict[starname]["fwhms"])
	colorarray = (fwhmarray / seeingarray)
	azarray = np.array(lcdict[starname]["azs"])
	#plt.scatter(mjdarray, magarray, c=pointsizes, label = starname)
	magarrays.append(magarray)
	colorarrays.append(colorarray)
	mjdarrays.append(mjdarray)
	azarrays.append(azarray)
	labels.append({"label": starname, "position": np.median(magarray)})


magarray = np.concatenate(magarrays)
colorarray = np.concatenate(colorarrays)
colorarray = np.clip(colorarray, 0.9, 1.3)
mjdarray = np.concatenate(mjdarrays)
azarray = np.concatenate(azarrays)

sc = plt.scatter(azarray, magarray, c=colorarray)
cb = plt.colorbar(sc)
cb.set_label("FWHM/s")

for label in labels:
	plt.text(np.min(mjdarray) - 0.05*(np.max(mjdarray) - np.min(mjdarray)), label["position"], label["label"])

ax = plt.gca() # gca means "get current axes", it returns the axes object.
# We invert the limits of the y axis in a perfectly natural way :
ax.set_ylim(ax.get_ylim()[::-1])
plt.xlabel("MJD [Days]")
plt.xlabel("Az [deg]")
plt.ylabel("Magnitude (relative)")
#plt.legend()
plt.show()
	
	
