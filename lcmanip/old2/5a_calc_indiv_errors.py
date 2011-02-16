#
#	A first try to calculate some errors based on the 
#	spread of stars around their median
#
#	Yes, some parts of this are very similar to the renormalization.
#	But this time, instead of taking the mean of median of the coeffs,
#	we use their spread.
#
#	We will write an error into the database. Warning : it is expressed in magnitudes.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# which sources do you want to use (give (deckey, sourcename) ):
refsources = [('dec_full1_1_medcoeff_1234', '1'),
('dec_full1_2_medcoeff_1234', '1'),
('dec_full2_5_medcoeff_1234', '5'),
('dec_full1_6_medcoeff_1234', '6')]

# a name for the error (in magnitudes !)  :
errorname = "magerror_1256"

# give the error you would like to use if only one *source* is available for that image :
onlyone_error = 0.1

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

errorcommentfieldname = errorname + "_comment"

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
#from combibynight_fct import *
#from star import *

from numpy import *
import matplotlib.pyplot as plt

print "This script needs to be configured in the source."
proquest(askquestions)


db = KirbyBase()

# Sort them like this, to ensure that points of one night are side by side (looks better on graphs ...)
allimages = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mhjd'])

print "I will try to calculate errors for", len(allimages), "images."

# Add a new temporary field to the dicts
for image in allimages:
	image["tmp_indivcoeffs"] = []	# yes, it's the same concept as for the renormalization.
	image["tmp_errorcomment"] = []


# A new list of dicts, to prepare the plots
plotdb = []

for refsource in refsources:
	deckey = refsource[0]
	sourcename = refsource[1]
	deckeyfilenumfield = "decfilenum_" + deckey
	intfieldname = "out_" + deckey + "_" + sourcename + "_int"
	
	# we start by calculating some statistics for the available fluxes :
	
	images = [image for image in allimages if image[deckeyfilenumfield] != None]
	print "%20s %5s : %4i deconvolutions available" % (deckey, sourcename, len(images))
	
	mags = -2.5 * log10(asarray(map(lambda x: x[intfieldname], images)))
	
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
		if image[deckeyfilenum] != None: # then we have a deconvolution
			mag = -2.5 * log10(image[intfieldname])
			indivcoeff = mag - medmag
			
			image["tmp_indivcoeffs"].append(indivcoeff)
			image["tmp_errorcomment"].append(sourcename + "/" + deckey)
			
			nums.append(i)	# for the plot
			indivcoeffs.append(indivcoeff)
	
	
	plotdb.append({"sourcename":sourcename, "deckey":deckey, "medmag":medmag, "nums":nums, "indivcoeffs":indivcoeffs})
	
	
proquest(askquestions)


# Now we go throug all the images, see which coefficients are available, and calculate their spread :
# The database is still no modified yet.

nums = [] # these are for the plots only, again
errors = []

for i, image in enumerate(allimages):
	nbcoeffs = len(image["tmp_indivcoeffs"])
	
	if nbcoeffs == 0:
		error = 0.0
	elif nbcoeffs == 1:
		error = onlyone_error
		
		nums.append(i) # these two lists are only for the plot
		errors.append(error)
	else :
		error = std(array(image["tmp_indivcoeffs"]))
		
		if nbcoeffs == 2:
			error = error * 1.8
		if nbcoeffs == 3:
			error = error * 1.3
		if nbcoeffs == 4:
			error = error * 1.2
		if nbcoeffs == 5:
			error = error * 1.15
		if nbcoeffs == 6:
			error = error * 1.1		
		
		nums.append(i) # these two lists are only for the plot
		errors.append(error)
		
	image["tmp_error"] = error # *this* is the important value, it will perhaps be written to the db later.
	# now each image has such a tmp_coeff.


# We are ready for a plot :
plt.figure(figsize=(12,8))	# sets figure size

for source in plotdb:
	
	label = source["sourcename"] + "/" + source["deckey"]
	plt.plot(source["nums"], source["indivcoeffs"], linestyle="None", marker=".", label = label)

# we add the calculated coefficients :

#plt.plot(nums, errors, linestyle="None", marker=".", label = "coeffs", color="black")
plt.errorbar(array(nums), zeros(len(nums)), array(errors), linestyle="None", marker=".", color="black")

# as a bonus, we could add the limits of the setnames ...

# and show the plot

ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])	# invert y axis

plt.xlabel('Images (by setname, then date)')
plt.ylabel('Magnitude')

plt.grid(True)
plt.legend()
plt.show()


# If you want, you can now write this into the database.

print "Ok, I would now add these errors to the database."
proquest(askquestions)

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, "error_"+errorname)

if errorname in db.getFieldNames(imgdb):
	print "The field", errorname, "already exists in the database."
	print "I will erase it."
	proquest(askquestions)
	db.dropFields(imgdb, [errorname, errorcommentfieldname])

db.addFields(imgdb, ['%s:float' % errorname, '%s:str' % errorcommentfieldname])

for i, image in enumerate(allimages):
	print i, image["imgname"], image["tmp_error"], image["tmp_errorcomment"]
	db.update(imgdb, ['recno'], [image['recno']], {errorname: float(image["tmp_error"]), errorcommentfieldname: " ".join(image["tmp_errorcomment"])})
	
db.pack(imgdb) # to erase the blank lines


	
