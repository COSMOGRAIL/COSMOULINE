execfile("../config.py")
from kirbybase import KirbyBase, KBError
import matplotlib.pyplot as plt
import numpy as np
from variousfct import *
from star import *

fieldname_deckeyfilenum = "decfilenum_dec_full_b_medcoeff_ab1"
fieldname_flux = "out_dec_full_b_medcoeff_ab1_b_flux"
star_name = "b"

db = KirbyBase()
images = db.select(imgdb, [fieldname_deckeyfilenum], ['\d\d*'], returnType='dict', sortFields=['mjd'], useRegExp=True)
# So we have sorted the images by date (important !)

# We "extract" what we want to plot :
fluxnorm_ad = np.array([float(image[fieldname_flux]) for image in images])	# This is a flux normalized,i.e the output of MCS
magsnorm_ad = -2.5 * np.log10(fluxnorm_ad)

flux_ad = np.array([float(image[fieldname_flux]/image["medcoeff"]) for image in images])	# this the clean flux
mags_ad = -2.5 * np.log10(flux_ad)


xcoords = np.arange(len(images))

# For the simulate images, we want to see a lightcurve before the deconvolution so we read the sextracor catalog produce to calculate the medcoeff (photometry aperture)

# we read the handwritten star catalog to identify the stars in the sextractor cat
alistars = readmancatasstars(alistarscat)	#must be a catalog where all the star I use are

list_flux_mjd = []	#list to add the flux and the mjd of the star we want

for i, image in enumerate(images):
	
	# the catalog we will read
	sexcat = alidir + image['imgname'] + ".alicat"
	
	# read sextractor catalog
	catstars = readsexcatasstars(sexcat)
		
	# cross-identify the stars with the handwritten selection
	identstars = listidentify(alistars, catstars, 5.0)
	
	for star in identstars:
		if star.name == star_name:
			list_flux_mjd.append({'flux': star.flux, 'mjd':image['mjd'], 'fluxnorm': star.flux * image['medcoeff']})

flux_bd = np.array([float(star['flux']) for star in list_flux_mjd])
mags_bd = -2.5 * np.log10(flux_bd)

fluxnorm_bd = np.array([float(star['fluxnorm']) for star in list_flux_mjd])
magsnorm_bd = -2.5 * np.log10(fluxnorm_bd)

# The reference star-------------------------------------------------------------

refmags = np.linspace(17.5,19,60) - 32.16

# And the plots :-----------------------------------------------------------------

plt.figure()

plt.plot(xcoords, mags_ad,label = "after deconv", color = 'b', marker = '.' )
plt.plot(xcoords, mags_bd,label = "before deconv", color = 'r', marker = '.')
plt.plot(xcoords, refmags,label = "reference magnitude", color = 'g', marker = '.')

# Reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])


plt.title('magnitude of star %s in time' %star_name, fontsize = 20)
plt.xlabel('Image number')
plt.ylabel('Magnitude')

plt.legend()

plt.figure()

ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.plot(xcoords, magsnorm_ad,label = "after deconv", color = 'b', marker = ".")
plt.plot(xcoords, magsnorm_bd,label = "before deconv", color = 'r', marker = ".")
plt.plot(xcoords, refmags,label = "reference magnitude", color = 'g', marker = '.')

plt.title('normalized magnitude of star %s in time (MSC output)' %star_name, fontsize = 20)
plt.xlabel('Image number')
plt.ylabel('Magnitude')

plt.legend()

plt.show()



# Some statistical computation

diff_magad_magbd = np.abs(mags_ad-mags_bd)

mean_diff = np.mean(diff_magad_magbd)
std_diff = np.std(diff_magad_magbd)

print "\nMean difference: ", mean_diff
print "Std difference: ", std_diff







