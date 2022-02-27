"""
Create the obj_star.cat files from the photomstar catalog.
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
from modules import star
from modules.variousfct import proquest

askquestions = settings['askquestions']
lensregion = settings['lensregion']


# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print("I will write individual coordinates catalogs for the following stars:")
print([s.name for s in photomstars])
proquest(askquestions)

# the stars
for s in photomstars:
    if not os.path.isfile(os.path.join(configdir, "obj_%s.cat" % s.name)):
        file = open(os.path.join(configdir, "obj_%s.cat" % s.name), 'w')
        file.write(f"{s.name}\t{s.x}\t{s.y}\t{s.flux}")
        file.close()


# and the lens
if not os.path.isfile(os.path.join(configdir, "obj_lens.cat")):
    file = open(os.path.join(configdir, "obj_lens.cat"), 'w')
    lenscoords = [lensreg.split(':') for lensreg in lensregion.split(',')]

    xlens = (float(lenscoords[0][0][1:]) + float(lenscoords[0][1])) / 2.0
    ylens = (float(lenscoords[1][0]) + float(lenscoords[1][1][:-1])) / 2.0

    file.write("lens" + '\t' + str(xlens) + '\t' + str(ylens) + '\t')
    file.close()