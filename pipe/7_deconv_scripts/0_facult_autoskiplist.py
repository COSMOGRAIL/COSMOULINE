#	Tiny helper to ouput a list of images to skip for a particular deconvolution, according to very simple criteria specified below.
#	This is perfectly facultative !

#	Do this for the lens, no need to run it for the renormalization stars etc (as the bad images will be skiped for the lens anyway)


execfile("../config.py")
from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *


########## Configuration #########

showhist = False
maxseeing = 2.2
maxell = 0.3
maxmedcoeff = 2.0
maxsky = 3500.0

##################################


print "You can configure some lines right at the beginning of this script."



import numpy as np
import matplotlib.pyplot as plt

db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict', sortFields=['setname', 'mjd'])

if os.path.isfile(decskiplist):
	print "You already have a decskiplist."
	print "In this script I will only consider images that are not yet rejected by this decskiplist."
	decskipimgnames = [image[0] for image in readimagelist(decskiplist)] # image[1] would be the comment
	images = [image for image in images if image["imgname"] not in decskipimgnames]
	print "Full path to decskiplist :"
else:
	cmd = "touch " + decskiplist
	os.system(cmd)
	print "I have just touched the decskiplist for you :"
print decskiplist

print "Note that here I do not look at a particular extracted object, but at the full database."
print "Looking at which object / PSFs are available for each image will be done in the next script."
print "We have %i images with gogogo=True, treatme=True, and not yet on the decskiplist." % ( len(images) )


proquest(askquestions)

if showhist :
	setnames = list(set([image["setname"] for image in images]))
	print "Setnames : %s" % (", ".join(setnames))

	print "Some histograms. Close the graphs to continue."
	plt.figure(1)
	seeinglists = [np.array([image["seeing"] for image in images if image["setname"] == setname]) for setname in setnames]
	plt.hist(seeinglists, bins=30)
	plt.axvline(maxseeing, color="red")
	plt.xlabel("Seeing [arcsec]")

	plt.figure(2)
	elllists = [np.array([image["ell"] for image in images if image["setname"] == setname]) for setname in setnames]
	plt.hist(elllists, bins=30)
	plt.axvline(maxell, color="red")
	plt.xlabel("Ellipticity")

	plt.figure(3)
	medcoefflists = [np.array([image["medcoeff"] for image in images if image["setname"] == setname]) for setname in setnames]
	plt.hist(medcoefflists, bins=30)
	plt.axvline(maxmedcoeff, color="red")
	plt.xlabel("Medcoeff")

	plt.figure(4)
	skylists = [np.array([image["skylevel"] for image in images if image["setname"] == setname]) for setname in setnames]
	plt.hist(skylists, bins=30)
	plt.axvline(maxsky, color="red")
	plt.xlabel("Sky level")
	
	plt.show()



print "\nHere are the images that do not satisfy your criteria (order of rejection : seeing, ell, medcoeff) :\n\n\n"
 

rejlines = []
rejectimages = [image for image in images if image["seeing"] > maxseeing]
rejlines.extend(["%s\t\t%s" % (image["imgname"], "seeing = %.2f arcsec" % image["seeing"]) for image in rejectimages])
images = [image for image in images if image not in rejectimages] # The "remaining" images
rejectimages = [image for image in images if image["ell"] > maxell]
rejlines.extend(["%s\t\t%s" % (image["imgname"], "ell = %.2f" % image["ell"]) for image in rejectimages])
images = [image for image in images if image not in rejectimages] # The "remaining" images
rejectimages = [image for image in images if image["medcoeff"] > maxmedcoeff]
rejlines.extend(["%s\t\t%s" % (image["imgname"], "medcoeff = %.2f" % image["medcoeff"]) for image in rejectimages])
images = [image for image in images if image not in rejectimages] # The "remaining" images
rejectimages = [image for image in images if image["skylevel"] > maxsky]
rejlines.extend(["%s\t\t%s" % (image["imgname"], "skylevel = %.2f" % image["skylevel"]) for image in rejectimages])
images = [image for image in images if image not in rejectimages] # The "remaining" images


print "# Autoskiplist made with maxseeing = %.3f, maxell = %.3f, maxmedcoeff = %.3f, maxsky = %.1f ." % (maxseeing, maxell, maxmedcoeff, maxsky)
print "# It contains %i images." % len(rejlines)
print "\n".join(rejlines)

print "\n\n\nCopy and paste this into your decskiplist, if you want to skip them."

