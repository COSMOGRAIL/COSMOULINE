############################################################################################################
########
######## LIGHT CURVE PER EXPOSURE, NORMALISED BY A NORMCOEFF OF YOUR CHOICE
########
############################################################################################################
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np
import os,sys
import headerstuff
import combibynight_fct
import matplotlib
import matplotlib.pyplot as plt


def simplemediancoeff(refidentstars, identstars):
	"""
	calculates a simple (but try to get that better ... it's pretty good !) multiplicative coeff for each image
	"calc one coef for each star and take the median of them"
	coef = reference / image
	"""

	coeffs = []
	for refstar in refidentstars:
		for star in identstars:
			if refstar.name != star.name:
				continue
			coeffs.append(refstar.flux / star.flux)
			break

	coeffs = np.array(coeffs)
	if len(coeffs) > 0:
		return len(coeffs), float(np.median(coeffs)), float(np.std(coeffs)), float(np.max(coeffs) - np.min(coeffs))
	else:
		return 0, 1.0, 99.0, 99.0


catalog = 'obj_quasar.cat'
# catalog = 'photomstar.cat'
sets= ['1']
ref_images=["1_ECAM.2019-11-23T02:44:37.000"]

db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')
nbrofimages = len(images)
print("I respect treatme, saturatedlist and other keywords defined in the script, and selected only %i images" % (nbrofimages))
# print(db.getFieldNames(imgdb))


# Read the manual star catalog :
objectcatpath = os.path.join(configdir, catalog)
normstarscatpath = os.path.join(configdir, "photomstars.cat")
object = star.readmancat(objectcatpath)
if len(object) > 1 :
	print("I can't treat more than one object at a time ! Please put only one object in your catalog.")
	exit()
else :
	object = object[0]
	print("Selected object : ")
	print(object)
normstars = star.readmancat(normstarscatpath)


xkeyword = 'mjds'  # default : mjds. Can also be moondists or hourangles
aperture = 'auto'  # for 30, put ap30
fluxfieldname = 'sexphotom1_quasar_auto_flux'
fluxerrfieldname = 'sexphotom1_quasar_auto_flux_err'
normkey = "medcoeff"

print("These is the subset of photom stars I will treat here :")
print("Aperture is defined as: %s" % aperture)
#proquest(askquestions)

# transform mydates in mjds\
# mydates = ["2016-10-01"]
# mymjds = []
# for date in mydates:
# 	mymjds.append(round(juliandate(datetime.datetime.strptime(str(date + "T23:59:59"), "%Y-%m-%dT%H:%M:%S")) - 2400000.5))

colors = ['crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow', 'crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow', 'crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow']

# get all obsnights
dates = sorted(list(set([image["date"] for image in images])))
mjds = sorted(list(set([round(image["mjd"]) for image in images])))
color = ['b', 'g', 'r', 'm', 'k', 'y']
# Compute the mag and magerr, and normalise them with respect to a normalisation coefficient.
# Plot per exposure, for a given date.

if 1:
	for s,st in enumerate(sets) :
		print("Set : ",s)
		setimages = [image for image in images if image['setname'] == st]

		groupedimages = combibynight_fct.groupbynights(setimages)
		mags = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=normkey, verbose =False )['median']
		absfluxerrors = np.array(combibynight_fct.values(groupedimages, fluxerrfieldname, normkey=normkey)['median'])
		fluxvals = np.array(combibynight_fct.values(groupedimages, fluxfieldname, normkey=normkey)['median'])
		mhjds_mags = combibynight_fct.values(groupedimages, 'mhjd', normkey=None)['mean']

		upmags = -2.5 * np.log10(fluxvals + absfluxerrors)
		downmags = -2.5 * np.log10(fluxvals - absfluxerrors)
		magerrorbars = (downmags - upmags) / 2.0

		print("%i nights" % len(groupedimages))

		# nbrofimages = len(setimages)
		#
		# refsexcat = os.path.join(alidir, ref_images[s] + ".alicat")
		# refcatstars = star.readsexcat(refsexcat,
		# 							  propfields=["FLUX_APER", "FLUX_APER1", "FLUX_APER2", "FLUX_APER3", "FLUX_APER4"])
		#
		# id = star.listidentify(normstars, refcatstars, tolerance=identtolerance)
		# refidentstars = id["match"]
		#
		# fluxes = []
		# mhjds = []
		# medcoeffs = []

		# for i, image in enumerate(setimages):
		#
		# 	print("- " * 30)
		# 	print(i + 1, "/", nbrofimages, ":", image['imgname'])
		#
		# 	# the catalog we will read
		# 	sexcat = os.path.join(alidir, image['imgname'] + ".alicat")
		#
		# 	# read sextractor catalog
		# 	catstars = star.readsexcat(sexcat, maxflag=0, posflux=True)
		# 	if len(catstars) == 0:
		# 		print("No stars in catalog !")
		# 		continue
		#
		# 	# cross-identify the stars with the handwritten selection
		# 	identstars = star.listidentify(normstars, catstars, 5.0)["match"]
		#
		# 	# calculate the normalization coefficient
		# 	nbrcoeff, medcoeff, sigcoeff, spancoeff = simplemediancoeff(refidentstars, identstars)
		# 	print("nbrcoeff :", nbrcoeff)
		# 	print("medcoeff :", medcoeff)
		# 	print("sigcoeff :", sigcoeff)
		# 	print("spancoeff :", spancoeff)
		#
		# 	print(image["%s_%s_%s_flux" % (sexphotomname, object.name, aperture)])
		# 	try :
		# 		fluxes.append(float(image["%s_%s_%s_flux" % (sexphotomname, object.name, aperture)]) / medcoeff)
		# 	except :
		# 		fluxes.append(np.nan)
		# 	mhjds.append(image['mhjd'])
		# 	medcoeffs.append(medcoeff)
		#
		# mags = -2.5 * np.log10(fluxes)
		# plt.figure(1)
		# plt.title("set : %s"%st)
		# plt.scatter(mhjds,mags, s=30)
		#
		# plt.figure(2)
		# plt.title("Medcoeff set : %s"%st)
		# plt.scatter(mhjds,medcoeffs, s=30)

		plt.figure(3)
		plt.grid(True)
		plt.errorbar(mhjds_mags, mags,yerr=magerrorbars,  fmt='+', color=color[s])
		plt.show()






