"""
Mag vs. MJD
Relies on info in settings.py
Does not bin the measurements by nights.
"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
import variousfct
import star
import numpy as np
import matplotlib.pyplot as plt

print "You want to analyze the deconvolution %s" %deckey
print "Deconvolved object : %s" % decobjname
print "I will use the normalization coeffs used for the deconvolution."

ptsources = star.readmancat(ptsrccat)
print "Number of point sources : %i" % len(ptsources)
print "Names of sources : %s" % ", ".join([s.name for s in ptsources])

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True)


plt.figure(figsize=(12,8))	# sets figure size

for s in ptsources:

	mags = -2.5*np.log10(np.array([image["out_%s_%s_flux" % (deckey, s.name)]*image[deckeynormused] for image in images]))
	mhjds = np.array([image["mhjd"] for image in images])
	
	plt.plot(mhjds, mags, linestyle="None", marker=".", label = s.name)

plt.grid(True)

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])

plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

#plt.legend()
leg = ax.legend(loc='best', fancybox=True)
leg.get_frame().set_alpha(0.5)
plt.show()

	
