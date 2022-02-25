"""
Little helper that creates the psfstars.cat files from the alistar catalog and the psfname
"""



import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import configdir, settings
from modules.variousfct import proquest
from modules import star


psfname = settings['psfname']
askquestions = settings['askquestions']

# Read the manual star catalog :
alistarscatpath = os.path.join(configdir, "psfstars.cat")
alistars = star.readmancat(alistarscatpath)

psfnamestars = [e for e in psfname] # we assume psfname is only the list of stars, named with only 1 letter (no aa or other funny stuff)

mystars = [s for s in alistars if s.name in psfnamestars]

print("I will write individual coordinates catalogs for the following stars:")
print([star.name for star in mystars])
proquest(askquestions)

# the stars
if os.path.isfile(os.path.join(configdir, "psf_%s.cat" % psfname)):
	print("The psf catalog already exists ! I stop here.")
	sys.exit()
else:
	file = open(os.path.join(configdir, "psf_%s.cat" % psfname), 'w')
	for s in mystars:
		file.write(s.name + '\t' + str(s.x) + '\t' + str(s.y) + '\t' + str(s.flux)+'\n')
	file.close()
