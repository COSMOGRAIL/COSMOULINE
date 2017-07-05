"""
Little helper that creates the psfstars.cat files from the alistar catalog and the psfname
"""


execfile("../config.py")
from variousfct import *
import star
import os,sys


# Read the manual star catalog :
alistarscatpath = os.path.join(configdir, "alistars.cat")
alistars = star.readmancat(alistarscatpath)

psfnamestars = [e for e in psfname] # we assume psfname is only the list of stars, named with only 1 letter (no aa or other funny stuff)

mystars = [s for s in alistars if s.name in psfnamestars]

print "I will write individual coordinates catalogs for the following stars:"
print [star.name for star in mystars]
proquest(askquestions)

# the stars
if os.path.isfile(os.path.join(configdir, "psf_%s.cat" % psfname)):
	print "The psf catalog already exists ! I stop here."
	sys.exit()
else:
	file = open(os.path.join(configdir, "psf_%s.cat" % psfname), 'w')
	for star in mystars:
		file.write(star.name + '\t' + str(star.x) + '\t' + str(star.y) + '\t' + str(star.flux)+'\n')
	file.close()
