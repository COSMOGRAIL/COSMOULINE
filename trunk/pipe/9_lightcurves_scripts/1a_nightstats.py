#
#	A sample script with some stats related to the combinations by-night.
#	IT RELIES ON THE DECONVOLUTION INFORMATION GIVEN IN SETTINGS.PY !
#	

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
from combibynight_fct import *
from star import *

from numpy import *
import matplotlib.pyplot as plt


print "You want to analyze the deconvolution %s" %deckey
print "Deconvolved object :", decobjname
print "Decfilenum field name : ", deckeyfilenum

# We read params of point sources
ptsrc = readmancatasstars(ptsrccat)
nbptsrc = len(ptsrc)
print "Number of point sources :", nbptsrc
print "Names of sources : "
for src in ptsrc: print src.name

db = KirbyBase()

# the \d\d* is a trick to select both 0000-like and 000-like
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True)
#images = db.select(imgdb, [deckeyfilenum, "telescopename"], ['\d\d*', "Mercator"], returnType='dict', useRegExp=True)

print "Number of images :", len(images)

mixedgroups = groupbynights(images, separatesetnames=False)
print "Number of nights (mixed setnames) :", len(mixedgroups)

unmixedgroups = groupbynights(images)
print "Number of nights (separate setnames)", len(unmixedgroups)


# Ok, now can could do a lot of statistics. For instance some histograms :
# Some control calculations
mixednightspans = map(nightspan, mixedgroups)
unmixednightspans = map(nightspan, unmixedgroups)
print "Maximum night span (mixed) :", max(mixednightspans), "hours."
print "Maximum night span (unmixed) :", max(unmixednightspans), "hours."

mixednightlenghts = map(len, mixedgroups)
mixedhisto = [(length, mixednightlenghts.count(length)) for length in sorted(list(set(mixednightlenghts)))]
print "mixedhisto", mixedhisto

unmixednightlenghts = map(len, unmixedgroups)
unmixedhisto = [(length, unmixednightlenghts.count(length)) for length in sorted(list(set(unmixednightlenghts)))]
print "unmixedhisto", unmixedhisto

# look in detail at some large nights ...
#largenights = [night for night in unmixedgroups if len(night) > 10]
#for largenight in largenights:
#	print len(largenight)
#	for image in largenight:
#		print image["date"], image["setname"]
		
		





