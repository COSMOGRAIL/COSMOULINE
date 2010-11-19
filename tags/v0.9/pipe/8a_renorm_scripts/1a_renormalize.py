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




execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
#from combibynight_fct import *
#from star import *

from numpy import *
import matplotlib.pyplot as plt

print "You want to calculate a renormalization coefficient called :"
print renormname
print "using the sources"
for renormsource in renormsources:
	print renormsource

db = KirbyBase()

# Sort them like this, to ensure that points of one night are side by side (looks better on graphs ...)
allimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mhjd'])

print "I will try to calculate a coefficient for", len(allimages), "images."

print "Before adding anything to the database, I will make a plot."
proquest(askquestions)

# Add a new temporary field to the dicts
for image in allimages:
	image["tmp_indivcoeffs"] = []
	image["tmp_coeffcomment"] = []


# A new list of dicts, to prepare the plots
plotdb = []

for renormsource in renormsources:
	deckey = renormsource[0]
	sourcename = renormsource[1]
	sourcedecnormfieldname = "decnorm_" + deckey
	deckeyfilenumfield = "decfilenum_" + deckey
	fluxfieldname = "out_" + deckey + "_" + sourcename + "_flux"
	
	# we start by calculating some statistics for the available fluxes :
	
	images = [image for image in allimages if image[deckeyfilenumfield] != None]
	print "%20s %5s : %4i deconvolutions available" % (deckey, sourcename, len(images))
	
	coeffs = asarray(map(lambda x: x[sourcedecnormfieldname], images))
	fluxes = asarray(map(lambda x: x[fluxfieldname], images))
	medflux = median(fluxes/coeffs) # so this median always refers to the "raw" fluxes, before any normalization
	
	mags = -2.5 * log10(fluxes/coeffs)
	# note that all this mag stuff is just for the plots.
	# the coeff will be written as multiplicative in flux.
	# again, we divide by the coeffs to come back to the raw fluxes before any normalization.
	
	meanmag = mean(mags)
	medmag = median(mags)
	stddevmag = std(mags)
	
	print "Mean mag :", meanmag
	print "Median mag :", medmag
	print "Stddev mag :", stddevmag
	
	# and now we go through *all*images, and update the indivcoeff field :
	
	nums = [] # these are for the plots only
	indivcoeffs = []
	
	for i, image in enumerate(allimages):
		if image[deckeyfilenumfield] != None: # then we have a deconvolution
		
			thiscoeff = image[sourcedecnormfieldname] 	# the coeff used for this deconvolution
			
			thisflux = image[fluxfieldname]/thiscoeff		# the intensity in the "raw" image
			
			indivcoeff = (medflux / thisflux) 		# the "new" absolute coeff for that image and star
			
			
			image["tmp_indivcoeffs"].append(indivcoeff)
			image["tmp_coeffcomment"].append(sourcename + "/" + deckey)
			
			nums.append(i)	# for the plot
			indivcoeffs.append(indivcoeff)
	
	
	plotdb.append({"sourcename":sourcename, "deckey":deckey, "medmag":medmag, "nums":nums, "indivcoeffs":indivcoeffs})
	
	
proquest(askquestions)


# Now we go throug all the images, see which coefficients are available, and calculate our coeff :
# The database is still no modified yet.

nums = [] # these are for the plots only, again
coeffs = []

for i, image in enumerate(allimages):
	
	if len(image["tmp_indivcoeffs"]) == 0:
		# bummer. Then we will just write 1.0
		renormcoeff = 1.0
		image["tmp_coeffcomment"].append("No star available.")
	else :
		renormcoeff = median(array(image["tmp_indivcoeffs"])) # median of multiplicative factors
		
		nums.append(i) # this is only for the plot
		coeffs.append(renormcoeff)
		
	image["tmp_coeff"] = renormcoeff # the important value at this step.
	# now each image has such a tmp_coeff.


# We are ready for a first plot, to compare the stars :
plt.figure(figsize=(12,8))	# sets figure size

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
plt.show()


# Great. You can now close this plot. 
# In a second plot we compare this new renormalization with the medcoeffs.
# To do this, we will first rescale the renormalization coeffs so that the reference image has coeff 1.0.

print "Rescaling coefficients with respect to reference image..."

refimage = [image for image in allimages if image["imgname"] == refimgname][0]

if len(refimage["tmp_indivcoeffs"]) == 0:
	print "OMFG !!! You did not deconvolve the reference image."
	print "Warning : I will not scale the renormalization coeffs, you better know what you are doing."

refnewcoeff = refimage["tmp_coeff"]
print "Renormalization coeff of the reference image with respect to the median level of all images :"
print refnewcoeff
print "(This should typically be around 1.0, but deviations are not a problem, they would mean that your reference image has atypical fluxes.)"
proquest(askquestions)

for i, image in enumerate(allimages):
	
	image["renormcoeff"] = image["tmp_coeff"] / refnewcoeff


# Time for the second plot, to compare these to the medcoeffs.

plt.figure(figsize=(12,8))	# sets figure size

medcoeffs = array([image["medcoeff"] for image in allimages])
renormcoeffs = array([image["renormcoeff"] for image in allimages])


plt.plot(medcoeffs, linestyle="None", marker=".", label = "medcoeff", color="black")
plt.plot(renormcoeffs, linestyle="None", marker=".", label = "renormcoeff", color="red")

# and show the plot

plt.xlabel('Images (by setname, then date)')
plt.ylabel('Coefficient')

plt.grid(True)
plt.legend()
plt.show()





# If you want, you can now write this into the database.

print "Ok, I would now add these coefficients to the database."
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, renormname)

if renormname in db.getFieldNames(imgdb):
	print "The field", renormname, "already exists in the database."
	print "I will erase it."
	proquest(askquestions)
	db.dropFields(imgdb, [renormname, renormcommentfieldname])

db.addFields(imgdb, ['%s:float' % renormname, '%s:str' % renormcommentfieldname])

for i, image in enumerate(allimages):
	#print i, image["imgname"], image["tmp_coeff"], image["tmp_coeffcomment"]
	db.update(imgdb, ['recno'], [image['recno']], {renormname: float(image["renormcoeff"]), renormcommentfieldname: " ".join(image["tmp_coeffcomment"])})
	
db.pack(imgdb) # to erase the blank lines

print "Ok, here you are."
	
