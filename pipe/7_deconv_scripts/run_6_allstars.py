execfile("../config.py")
import os
from variousfct import *
import star


readoutcatpath = os.path.join(configdir, "readoutstars.cat")
photomstars = star.readmancat(photomstarscatpath)

print "I will readout the following stars:"
print [star.name for star in photomstars]
proquest(True)

for star in photomstars :
    os.system("python 6_readout.py " + star.name)
