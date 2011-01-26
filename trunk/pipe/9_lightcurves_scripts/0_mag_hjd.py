#
#	For a deconvolution, does not combine the light curves by night to make a first plot.
#	This script shows the points of 1 deconvolution only, possibly with multiple sources.
#	Colouring is done according to source.
#	IT RELIES ON THE DECONVOLUTION INFORMATION GIVEN IN SETTINGS.PY !
#	
#	You will typically want to make custom plots for your lens later
#	This is just to give a first automatic view, without any configuration,
#	using the current settings of settings.py with which you did the deconvolution.
#
#	


execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star


from numpy import *
import matplotlib.pyplot as plt


print "You want to analyze the deconvolution %s" %deckey
print "Deconvolved object :", decobjname

# we read params of point sources
ptsrc = star.readmancat(ptsrccat)
nbptsrc = len(ptsrc)
print "Number of point sources :", nbptsrc
print "Names of sources : "
for src in ptsrc: print src.name

#proquest(askquestions)

db = KirbyBase()

# the \d\d* is a trick to select both 0000-like and 000-like
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True)

plt.figure(figsize=(12,8))	# sets figure size

for src in ptsrc:

	key = 'out_'+deckey+'_'+ src.name +'_flux'
	mags = -2.5*log10(asarray([image[key]*image["medcoeff"] for image in images]))
	
	mhjds = asarray([image["mhjd"] for image in images])
	
	plt.plot(mhjds, mags, linestyle="None", marker=".", label = src.name)

plt.grid(True)

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.title(deckey, fontsize=20)
plt.xlabel('Time [days]')
plt.ylabel('Magnitude')

plt.legend()
plt.show()

	
