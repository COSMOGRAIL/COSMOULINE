"""
Create the obj_star.cat files from the photomstar catalog.
"""


exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np
import os,sys
import f2n

# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print("I will write individual coordinates catalogs for the following stars:")
print([star.name for star in photomstars])
proquest(askquestions)

# the stars
for star in photomstars:
	if not os.path.isfile(os.path.join(configdir, "obj_%s.cat" % star.name)):
		file = open(os.path.join(configdir, "obj_%s.cat" % star.name), 'w')
		file.write(star.name + '\t' + str(star.x) + '\t' + str(star.y) + '\t' + str(star.flux))
		file.close()



# and the lens
if not os.path.isfile(os.path.join(configdir, "obj_lens.cat")):
	file = open(os.path.join(configdir, "obj_lens.cat"), 'w')
	lenscoords = [lensreg.split(':') for lensreg in lensregion.split(',')]

	xlens = (float(lenscoords[0][0][1:]) + float(lenscoords[0][1])) / 2.0
	ylens = (float(lenscoords[1][0]) + float(lenscoords[1][1][:-1])) / 2.0

	file.write("lens" + '\t' + str(xlens) + '\t' + str(ylens) + '\t')
	file.close()