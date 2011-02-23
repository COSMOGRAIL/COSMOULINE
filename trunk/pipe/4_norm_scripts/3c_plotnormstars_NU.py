
execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np
import calccoeff_fct

import matplotlib.pyplot as plt


db = KirbyBase()
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

nbrofimages = len(images)
print "I respect treatme, and selected only %i images" % (nbrofimages)

# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)
print "Photom stars :"
print "\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars])



# the maximum number of possible stars that could be used
maxcoeffstars = len(normstars)
print "Number of coefficient stars :", maxcoeffstars
nbrofimages = len(images)
print "I will treat", nbrofimages, "images."
proquest(askquestions)

for i, image in enumerate(images):
	
	
	
	# calculate the normalization coefficient
	nbrcoeff, medcoeff, sigcoeff, spancoeff = simplemediancoeff(refidentstars, identstars)
	print "nbrcoeff :", nbrcoeff
	print "medcoeff :", medcoeff
	print "sigcoeff :", sigcoeff
	print "spancoeff :", spancoeff
	
	db.update(imgdb, ['recno'], [image['recno']], {'nbrcoeffstars': nbrcoeff, 'maxcoeffstars': maxcoeffstars, 'medcoeff': medcoeff, 'sigcoeff': sigcoeff, 'spancoeff': spancoeff})

db.pack(imgdb) # to erase the blank lines

print "Done."




