#
#	Renormalization using deconvolved sources, on an image-by-image basis.
#	We will simply add a new multiplicative (in flux)
#	renormalization coefficient to the database, that "contains" the coefficient used
#	to deconvolve the stars you choose !
#	It will try to run on all images with gogogo = True and treatme = True.
#	If for some reason it cannot be calculated (typically as the given sources where not deconvolved
#	for this or that image etc), the field will be "1.0".
#	So there is no problem to mix up stars from differnent deconvolutions if you which.
#
#
#	Potentially we could add lots of other fields, like number of stars used and errors.
#
#	coef = reference / image
#	-> faint images get higher coef, you need to multiply an image by the coef to normalize it.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
#from combibynight_fct import *
#from star import *
import progressbar

import numpy as np
import matplotlib.pyplot as plt

print("You want to calculate a renormalization coefficient called :")
print(renormname)
print("using the sources")
for renormsource in renormsources:
	print(renormsource)

db = KirbyBase(imgdb)

# Sort them like this, to ensure that points of one night are side by side (looks better on graphs ...)
allimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mhjd'])

print("I will try to calculate a coefficient for", len(allimages), "images.")

print("Before adding anything to the database, I will make plots.")
proquest(askquestions)

# Add a new temporary field to the dicts
for image in allimages:
	image["tmp_indivcoeffs"] = []
	image["tmp_coeffcomment"] = []


# A new list of dicts, to prepare the plots
plotdb = []


# We go through the sources, one by one, and see for which image each source is available.

for renormsource in renormsources:
	deckey = renormsource[0]
	sourcename = renormsource[1]
	deckeyfilenumfield = "decfilenum_" + deckey
	fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
	errorfieldname = "out_" + deckey + "_" + sourcename + "_shotnoise"
	decnormfieldname = "decnorm_" + deckey
	
	# we start by calculating some statistics for the available fluxes :
	
	images = [image for image in allimages if image[deckeyfilenumfield] != None]
	print("%20s %5s : %4i deconvolutions available" % (deckey, sourcename, len(images)))
	
	fluxes = np.array([image[fluxfieldname] for image in images]) # So these are raw fluxes in electrons, not normalized
	decnormcoeffs = np.array([image[decnormfieldname] for image in images])
	
	# Now we want to find a very good "typical" flux (reference flux) for this particular star.
	# OLD To find which flux is "typcial", we analyse the normalized fluxes.
	# OLD But then, once we found the typical image of this star, we take the raw, non-normalized flux of this star on this image.
	
	
	normfluxes = fluxes*decnormcoeffs
	
	# There are logic errors in what follows ...
	"""
	sortindices = np.argsort(normfluxes)
	if len(images) <= 3:
		print "Hey, not enough images, this is not good, I might produce crap."
	medianindex = sortindices[int(sortindices.size / 2)]
	print "Median index : %i / %i" % (medianindex, sortindices.size)
	normmedflux = normfluxes[medianindex]
	# And finally, our NOT NORMALIZED reference flux :
	medflux = fluxes[medianindex]
	"""
	
	# ... so keep it simple :
	normmedflux = np.median(normfluxes) # This is not used for any calculation
	medflux = np.median(fluxes) # This is the plain simple unnormalized ref flux that we will use for this star.
	
	# showing these hists works fine, but we do this now directly after the deconvolution.
	"""
	plt.hist(fluxes, bins=100, color=(0.6, 0.6, 0.6))
	plt.hist(normfluxes, bins=100, color=(0.3, 0.3, 0.3))
	plt.axvline(normmedflux, color="black")
	plt.axvline(medflux, color="red")
	#plt.axvline(simplemedflux, color="blue")
	plt.title("Histogram of normalized flux : %s" % (sourcename + " / " + deckey))
	plt.xlabel("Normalized flux, electrons")
	plt.show()
	"""
	
	# Next step is just as information for the user to identify good and bad stars :
	mags = -2.5 * np.log10(fluxes*decnormcoeffs)
	# note that all this mag stuff is just for the plots.
	
	meanmag = np.mean(mags)
	medmag = np.median(mags)
	stddevmag = np.std(mags)
	
	print("Mean mag :", meanmag)
	print("Median mag :", medmag)
	print("Stddev mag :", stddevmag)
	print("(in electrons, given the normalization used for deconvolution)")
	
	# and now we go through *all*images, and update the indivcoeff field :
	
	nums = [] # these are for the plots only
	indivcoeffs = []
	mhjds = []
	fluxes = []
	errors = []
	
	for i, image in enumerate(allimages):
		if image[deckeyfilenumfield] != None: # then we have a deconvolution
		
			thisflux = image[fluxfieldname] # the intensity in the "raw" image
			
			indivcoeff = (medflux / thisflux) 	# the "new" absolute coeff for that image and star
			
			
			image["tmp_indivcoeffs"].append(indivcoeff)
			image["tmp_coeffcomment"].append(sourcename + " / " + deckey)
			
			nums.append(i)	# for the plot
			mhjds.append(image["mhjd"])
			fluxes.append(thisflux)
			errors.append(image[errorfieldname])
			indivcoeffs.append(indivcoeff)
	
	
	plotdb.append({"sourcename":sourcename, "deckey":deckey, "medmag":medmag, "nums":nums, "mhjds":mhjds, "fluxes":fluxes, "errors":errors, "indivcoeffs":indivcoeffs})
	
	
#proquest(askquestions)


# Now we go throug all the images, see which coefficients are available, and calculate our coeff :
# The database is still no modified yet.

nums = [] # these are for the plots only, again
coeffs = []

for i, image in enumerate(allimages):
	
	if len(image["tmp_indivcoeffs"]) == 0:
		# bummer. Then we will just write 0.0, to be sure that this one will pop out.
		renormcoeff = 0.0
		print("Image %s : no star available." % (image["imgname"]))
		image["tmp_coeffcomment"].append("No star available.")
		# we add nothing to coeffs
	else :
		renormcoeff = np.median(np.array(image["tmp_indivcoeffs"])) # median of multiplicative factors
		
		nums.append(i) # this is only for the plot
		coeffs.append(renormcoeff)
		
	image["tmp_coeff"] = renormcoeff # the important value at this step.
	# now each image has such a tmp_coeff.


# We are ready for a first plot, to compare the stars :
plt.figure(figsize=(15,15))	# sets figure size

for source in plotdb:
	
	label = source["sourcename"] + "/" + source["deckey"]
	plt.plot(source["nums"], source["indivcoeffs"], linestyle="None", marker=".", label = label)

# we add the calculated coefficients :

plt.plot(nums, coeffs, linestyle="None", marker=".", label = "Median of those coeffs", color="black")

# and show the plot

plt.xlabel('Images (by setname, then date)')
plt.ylabel('Coefficient')

plt.grid(True)
plt.legend()

if savefigs:
	plotfilepath = os.path.join(plotdir, "renorm_%s_indivcoeffs.pdf" % renormname)
	plt.savefig(plotfilepath)
	print("Wrote %s" % (plotfilepath))
else:
	plt.show()





# Great. You can now close this plot. 
# In a second plot we compare this new renormalization with the medcoeffs.
# To do this, we will first rescale the renormalization coeffs so that the reference image has coeff 1.0.

print("Rescaling coefficients with respect to reference image...")

refimage = [image for image in allimages if image["imgname"] == refimgname][0]

if len(refimage["tmp_indivcoeffs"]) == 0:
	print("OMFG !!! You did not deconvolve the reference image.")
	print("Warning : I will not scale the renormalization coeffs, you better know what you are doing.")

refnewcoeff = refimage["tmp_coeff"]
print("Renormalization coeff of the reference image with respect to the median level of all images :")
print(refnewcoeff)
print("(This should typically be around 1.0, but deviations are not a problem, they would mean that your reference image has atypical fluxes.)")
#proquest(askquestions)

for i, image in enumerate(allimages):
	
	image["renormcoeff"] = image["tmp_coeff"] / refnewcoeff


# Time for the second plot, to compare these to the medcoeffs.

plt.figure(figsize=(15,15))	# sets figure size

medcoeffs = np.array([image["medcoeff"] for image in allimages])
renormcoeffs = np.array([image["renormcoeff"] for image in allimages])


plt.plot(medcoeffs, linestyle="None", marker=".", label = "medcoeff", color="black")
plt.plot(renormcoeffs, linestyle="None", marker=".", label = renormname, color="red")

# and show the plot

plt.xlabel('Images (by setname, then date)')
plt.ylabel('Coefficient')

plt.grid(True)
plt.legend()

if savefigs:
	plotfilepath = os.path.join(plotdir, "renorm_%s_medcoeffcompa.pdf" % renormname)
	plt.savefig(plotfilepath)
	print("Wrote %s" % (plotfilepath))
else:
	plt.show()


# This is done in a separate script, now, also for other stars if you want.
"""
# Next plot, we show the plain lightcurves of the renormalization stars, "renormalized"


for renormsource in renormsources:
	
	plt.figure(figsize=(15,15))	# sets figure size

	
	deckey = renormsource[0]
	sourcename = renormsource[1]
	deckeyfilenumfield = "decfilenum_" + deckey
	fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
	errorfieldname = "out_" + deckey + "_" + sourcename + "_shotnoise"
	decnormfieldname = "decnorm_" + deckey
	renormfieldname = "renormcoeff"
	
	images = [image for image in allimages if image[deckeyfilenumfield] != None]
	
	fluxes = np.array([image[fluxfieldname] for image in images])
	errors = np.array([image[errorfieldname] for image in images])
	decnormcoeffs = np.array([image[decnormfieldname] for image in images])
	renormcoeffs = np.array([image[renormfieldname] for image in images])
	
	renormfluxes = fluxes*renormcoeffs
	renormerrors = errors*renormcoeffs
	ref = np.median(renormfluxes)
	
	mhjds = np.array([image["mhjd"] for image in images])
	label = sourcename + " / " + deckey
	
	#plt.plot(mhjds, renormfluxes/ref, linestyle="None", marker=".", label = label)
	plt.errorbar(mhjds, renormfluxes/ref, yerr=renormerrors/ref, ecolor=(0.8, 0.8, 0.8), linestyle="None", marker=".", label = label)

	plt.title("%s, using %s" % (label, renormname))
	plt.xlabel("MHJD")
	plt.ylabel("Flux in electrons / median")
	plt.grid(True)
	plt.ylim(0.95, 1.05)

	if savefigs:
		plotfilepath = os.path.join(plotdir, "renorm_%s_renormflux_%s.pdf" % (renormname, sourcename))
		plt.savefig(plotfilepath)
		print "Wrote %s" % (plotfilepath)
	else:
		plt.show()

"""

# If you want, you can now write this into the database.

print("Ok, I would now add these coefficients to the database.")
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, renormname)

if renormname in db.getFieldNames(imgdb):
	print("The field", renormname, "already exists in the database.")
	print("I will erase it.")
	proquest(askquestions)
	db.dropFields(imgdb, [renormname, renormcommentfieldname])

db.addFields(imgdb, ['%s:float' % renormname, '%s:str' % renormcommentfieldname])

widgets = [progressbar.Bar('>'), ' ', progressbar.ETA(), ' ', progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(allimages)+2).start()

for i, image in enumerate(allimages):
	#print i, image["imgname"], image["tmp_coeff"], image["tmp_coeffcomment"]
	pbar.update(i)
	db.update(imgdb, ['recno'], [image['recno']], {renormname: float(image["renormcoeff"]), renormcommentfieldname: " ".join(image["tmp_coeffcomment"])})

pbar.finish()

db.pack(imgdb) # to erase the blank lines

print("Ok, here you are.")
