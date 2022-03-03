import sys
import os
from subprocess import call
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import python, configdir
from modules.variousfct import proquest
import star


readoutcatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(readoutcatpath)

print("I will readout the following stars:")
print([star.name for star in photomstars])
proquest(True)


for s in photomstars :
    call([python, "6_readout.py", s.name])
