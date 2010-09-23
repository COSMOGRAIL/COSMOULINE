# This is just a little helper script, not required at all !
# We read in2.txt as resulting from the deconv, and translate it into
# what you would have to write in the ptsrc catalog file of the configdir.

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
from star import *
import numpy as np


in2filepath = os.path.join(decdir, "in2.txt")
in2file = open(in2filepath)
in2filelines = in2file.readlines()
in2file.close()

print "Reading from :"
print in2filepath

ptsrcs = readmancatasstars(ptsrccat)
nbptsrcs = len(ptsrcs)

#print in2filelines

# quick and dirty filtering of the trash ...
goodlines = []
for line in in2filelines:
	if line[0] == "-" or line[0] == "|":
		continue
	goodlines.append(line)

# we translate all this into a tiny db :

ptsrcdb = []
for (i, ptsrc) in enumerate(ptsrcs):
	xpos = (float(goodlines[2*i + 1].split()[0])+0.5)/2.0
	ypos = (float(goodlines[2*i + 1].split()[1])+0.5)/2.0
	influx = ptsrc.flux
	in2flux = float(np.median(map(float, np.array(goodlines[2*i].split()))))
	ptsrcdb.append({"name":ptsrc.name, "xpos":xpos, "ypos":ypos, "influx":influx, "in2flux":in2flux})


# And we print this out:


print "\nOutput astrometry with input photometry :"
print "\n".join(["%s\t%f\t%f\t%f" % (ptsrc["name"], ptsrc["xpos"], ptsrc["ypos"], ptsrc["influx"]) for ptsrc in ptsrcdb])

print "\nOutput astrometry and median output photometry :"
print "\n".join(["%s\t%f\t%f\t%f" % (ptsrc["name"], ptsrc["xpos"], ptsrc["ypos"], ptsrc["in2flux"]) for ptsrc in ptsrcdb])


