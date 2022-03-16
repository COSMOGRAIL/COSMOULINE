# This is just a little helper script, not required at all !
# We read in2.txt as resulting from the deconv, and translate it into
# what you would have to write in the ptsrc catalog file of the configdir.
import sys

if len(sys.argv) == 2:
	execfile("../config.py")
	decobjname = sys.argv[1]
	deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
	ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
	decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
	deckeyfilenum = "decfilenum_" + deckey
	deckeypsfused = "decpsf_" + deckey
	deckeynormused = "decnorm_" + deckey
	decdir = os.path.join(workdir, deckey)
	print "You are running the deconvolution on all the stars at once."
	print "Current star : " + sys.argv[1]

else:
	execfile("../config.py")

from kirbybase import KirbyBase, KBError
from variousfct import *
from readandreplace_fct import *
import star
import numpy as np



in2filepath = os.path.join(decdir, "in2.txt")
in2file = open(in2filepath)
in2filelines = in2file.readlines()
in2file.close()

print "Reading from :"
print in2filepath

ptsrcs = star.readmancat(ptsrccat)
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
	in2flux = float(np.median(map(float, np.array(goodlines[2*i].split()[1:])))) # we count the ref image only once here.
	ptsrcdb.append({"name":ptsrc.name, "xpos":xpos, "ypos":ypos, "influx":influx, "in2flux":in2flux})


# And we print this out:


print "\nOutput astrometry with input photometry :"
print "\n".join(["%s\t%f\t%f\t%f" % (ptsrc["name"], ptsrc["xpos"], ptsrc["ypos"], ptsrc["influx"]) for ptsrc in ptsrcdb])

print "\nOutput astrometry and median output photometry :"
print "\n".join(["%s\t%f\t%f\t%f" % (ptsrc["name"], ptsrc["xpos"], ptsrc["ypos"], ptsrc["in2flux"]) for ptsrc in ptsrcdb])


print "\nI can write the last version into your point star catalogue if you want"
proquest(askquestions)
cat = open(ptsrccat,'w')
for ptsrc in ptsrcdb:
	cat.write("\n%s\t%f\t%f\t%f" % (ptsrc["name"], ptsrc["xpos"], ptsrc["ypos"], ptsrc["in2flux"]))
cat.close()
print "OK, your point star catalogue is edited !"
"""
print "\nCopy this into your dec catalog:"
print "%s" % ptsrccat
print ""
"""