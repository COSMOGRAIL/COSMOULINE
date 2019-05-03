"""
We plot the evolution of the stuff over stuff for various lenses.
This works with a cosmouline database only (sorry)
"""

execfile("../config.py")  # probably not needed...
from kirbybase import KirbyBase, KBError
import numpy as np
import matplotlib.pyplot as plt
import sys


# load the database
lensname = "datatest"
imgdb = "/Users/martin/Desktop/COSMO3b/run/datatest_ECAM/database.dat"

db = KirbyBase()

images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', useRegExp=True, sortFields=['mjd'])

# keep only the images taken in UL
images = [i for i in images if "1_" in i["imgname"]]

# isolate the variables of interest
mhjds = np.array([image["mhjd"] for image in images])
ells = np.array([image["ell"] for image in images])
airmasses = np.array([image["airmass"] for image in images])
seeings = np.array([image["seeing"] for image in images])
pas = np.array([image["pa"] for image in images])
bimgs = np.array([image["bimage"] for image in images])
aimgs = np.array([image["aimage"] for image in images])
diffaxes = np.array(aimgs-bimgs)*[i["pixsize"] for i in images]


# cap the ellipticity
ells = np.array([e if e < 0.5 else 0.5 for e in ells])


# load the output of get_prered_vals.py
vals = np.load("valstemp_%s.npy"%lensname)
vals = [v for v in vals if v["imgname"] in [i["imgname"].split("_")[1] for i in images]]

# isolate the variables of interest from get_prered_vals.py for the images in the db
windspeeds = []
winddirs = []
azimuths = []
elevs = []
for i in images:
	try:
		val = [v for v in vals if v["imgname"] == i["imgname"].split("_")[1]][0]
		ws = float(val["windspeed"])
		wd = float(val["winddir"])
		azi = float(val["azi"])
		elev = float(val["elev"])

		# If one of these values is crazy, it means it has not been properly acquired in the header. We put null values instead

		#if ws > 100 or wd > 360:
		#	ws, wd = 0, 0

		windspeeds.append(ws)
		winddirs.append(wd)
		azimuths.append(azi)
		elevs.append(elev)
	except:
		windspeeds.append(-0)
		winddirs.append(-0)
		azimuths.append(0)
		elevs.append(0)


#np the shit our of these
windspeeds, winddirs, elevs = np.array(windspeeds), np.array(winddirs), np.array(elevs)
azimuths = np.array(azimuths)


# compute the wind angle. A bit tricky because of the 360deg modulo
# easiest way is to use astropy
from astropy import units as u
from astropy.coordinates import Angle, angle_utilities

windangles = [angle_utilities.angular_separation(azi, 0, wd, 0)*360./(2*3.1416) for wd, azi in zip(winddirs, azimuths)]

windangles = np.array(windangles)


# compute the altitude and elevation speed. Formula from Bruno
import math
elev_speeds = [math.cos(29*math.pi/180.) * math.sin(azi/180.*math.pi) for azi in azimuths]
azi_speeds = [(math.sin(-29*math.pi/180.) - (math.sin(-47*math.pi/180.) * math.cos(azi/180.*math.pi)))/math.sin(azi/180.*math.pi)**2 for azi in azimuths]
total_speed = [np.sqrt(e**2 + a**2) for e, a in zip(elev_speeds, azi_speeds)]



# Create an index of the good images (kick bad seeing, bad airmass, crazy wind)
# good_inds = [True if (0 < ws < 100 and am < 1.5 and see < 1.5)
#              else False
#              for ws, am, see in zip(windspeeds, airmasses, seeings)]

good_inds = [True
             for ws, am, see in zip(windspeeds, airmasses, seeings)]


# Ok, so now we have a bit of everything. Let's explore the correlations. Change the first value in the zip functions below to chose what you want
xs = [x for x, v in zip(total_speed, good_inds) if v is True]
ys = [y for y, v in zip(diffaxes, good_inds) if v is True]
cs = [c for c, v in zip(mhjds, good_inds) if v is True]


# if you want to write in a txt file
if 0:
	with open("x_vs_y.txt", "w") as f:
		#f.write("time\tA-B [arcsec]\n")  # header, adapt case by case
		for t, d in zip(xs, ys):
			f.write("%f\t%f\n" % (t, d))
		f.close()


# finally, the plot
cm = plt.cm.get_cmap('RdYlBu')
plt.figure()
sc = plt.scatter(xs, ys, c=cs, cmap=cm)
plt.colorbar(sc, label='mhjds')
plt.title(lensname)
plt.xlabel("total speed", fontsize=12)
plt.ylabel("A-B", fontsize=12)
#plt.axis([-0.1, 1.1, 0, 0.2])
plt.show()



