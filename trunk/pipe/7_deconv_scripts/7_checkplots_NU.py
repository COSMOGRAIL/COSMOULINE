"""
Some plots are created in the plotdir, they should allow to check for instance the convergence of the deconvolution.

"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import star
import numpy as np
import matplotlib.pyplot as plt


figbase = deckey


db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True) # The sorting is not important.

ptsrcs = star.readmancat(ptsrccat)
nbptsrcs = len(ptsrcs)
print "Number of point sources :", nbptsrcs
print "Names of sources : "
for src in ptsrcs: print src.name


# The parameters common to all sources


delta1fieldname = "out_" + deckey + "_delta1"
delta2fieldname = "out_" + deckey + "_delta2"
delta1s = np.array([image[delta1fieldname] for image in images])
delta2s = np.array([image[delta2fieldname] for image in images])
#(delta1min, delta1max) = (np.min(delta1s), np.max(delta1s))
#(delta2min, delta2max) = (np.min(delta2s), np.max(delta2s))
plt.figure(figsize=(12, 12))
ax = plt.gca()
ax.set_aspect('equal')
plt.scatter(delta1s, delta2s, s=1, color="blue")
plt.xlabel("Delta 1")
plt.ylabel("Delta 2")

plotname = figbase+"_delta.png"
plt.savefig(os.path.join(plotdir, plotname))
print "Wrote %s" % (plotname)


z1fieldname = "out_" + deckey + "_z1"
z2fieldname = "out_" + deckey + "_z2"
z1s = np.array([image[z1fieldname] for image in images])
z2s = np.array([image[z2fieldname] for image in images])
plt.figure(figsize=(12, 12))
plt.scatter(z1s, z2s, s=1, color="blue")
plt.xlabel("z1")
plt.ylabel("z2")
plotname = figbase+"_z.png"
plt.savefig(os.path.join(plotdir, plotname))
print "Wrote %s" % (plotname)


for src in ptsrcs:

	xfieldname = "out_" + deckey + "_" + src.name + "_x"
	yfieldname = "out_" + deckey + "_" + src.name + "_y"
	fluxfieldname = "out_" + deckey + "_" + src.name + "_flux"
	noisefieldname = "out_" + deckey + "_" + src.name + "_shotnoise"
	decnormfieldname = "decnorm_" + deckey
	
	
	
	fluxes = np.array([image[fluxfieldname] for image in images])
	decnormcoeffs = np.array([image[decnormfieldname] for image in images])
	
	normfluxes = fluxes*decnormcoeffs
	
	#plt.axvline(normmedflux, color="black")
	#plt.axvline(medflux, color="red")
	#plt.axvline(simplemedflux, color="blue")
	
	
	plt.figure(figsize=(12, 12))
	
	plt.hist(fluxes, bins=100, color=(0.6, 0.6, 0.6))
	plt.hist(normfluxes, bins=100, color=(0.3, 0.3, 0.3))
	plt.title("Histogram of normalized flux : %s" % (src.name + " / " + deckey))
	plt.xlabel("Normalized flux, electrons")
	
	
	plotname = figbase + "_" + src.name + "_fluxhist.png"
	plt.savefig(os.path.join(plotdir, plotname))
	print "Wrote %s" % (plotname)
