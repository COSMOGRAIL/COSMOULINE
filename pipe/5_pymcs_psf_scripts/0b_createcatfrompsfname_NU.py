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
from config import configdir, settings, normstarscat
from modules.variousfct import proquest
from modules import star


psfname = settings['psfname']
askquestions = settings['askquestions']

# Read the manual star catalog :
psfstars = star.readmancat(normstarscat)
# we assume psfname is only the list of stars, named with only 1 letter 
# (no aa or other funny stuff)
psfnamestars = [e for e in psfname] 

mystars = [s for s in psfstars if s.name in psfnamestars]

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
        file.write(f"{s.name}\t{s.x}\t{s.y}\t{s.flux}\n")
    file.close()
