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
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['setname', 'mhjd'])

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
plt.title("Delta scatter : %s" % (deckey))

if savefigs:
	plotfilepath = os.path.join(plotdir, "%s_check_delta.pdf" % figbase)
	plt.savefig(plotfilepath)
	print "Wrote %s" % (plotfilepath)
else:
	plt.show()


z1fieldname = "out_" + deckey + "_z1"
z2fieldname = "out_" + deckey + "_z2"
z1s = np.array([image[z1fieldname] for image in images])
z2s = np.array([image[z2fieldname] for image in images])
plt.figure(figsize=(12, 12))
plt.scatter(z1s, z2s, s=1, color="blue")
plt.xlabel("z1")
plt.ylabel("z2")
plt.title("Z scatter : %s" % (deckey))

if savefigs:
	plotfilepath = os.path.join(plotdir, "%s_check_z.pdf" % figbase)
	plt.savefig(plotfilepath)
	print "Wrote %s" % (plotfilepath)
else:
	plt.show()



for src in ptsrcs:

	# Flux histogram

	xfieldname = "out_" + deckey + "_" + src.name + "_x"
	yfieldname = "out_" + deckey + "_" + src.name + "_y"
	fluxfieldname = "out_" + deckey + "_" + src.name + "_flux"
	noisefieldname = "out_" + deckey + "_" + src.name + "_shotnoise"
	decnormfieldname = "decnorm_" + deckey
	
	fluxes = np.array([image[fluxfieldname] for image in images])
	decnormcoeffs = np.array([image[decnormfieldname] for image in images])
	
	normfluxes = fluxes*decnormcoeffs
	
	if len(normfluxes) > 15:
		sortnormfluxes = np.sort(normfluxes)
		diffs = sortnormfluxes[1:] - sortnormfluxes[:-1]
		borderdiffs = diffs[[0, 1, 2, 3, 4, -5, -4, -3, -2, -1]]
		percentborderdiffs = borderdiffs/np.median(normfluxes)*100.0
		lowflux  = "Low  : + " + " / ".join(["%.3f" % (bd) for bd in percentborderdiffs[:5]]) + " %"
		highflux = "High : + " + " / ".join(["%.3f" % (bd) for bd in percentborderdiffs[5:]]) + " %"
		print lowflux
		print highflux
	
	plt.figure(figsize=(12, 12))
	
	(mi, ma) = (np.min(normfluxes), np.max(normfluxes))
	plt.axvline(mi, ymin=0.1, color="red")
	plt.axvline(ma, ymin=0.1,color="red")
	plt.figtext(0.15, 0.85, highflux)
	plt.figtext(0.15, 0.83, lowflux)
	plt.hist(fluxes, bins=200, color=(0.6, 0.6, 0.6))
	plt.hist(normfluxes, bins=200, color=(0.3, 0.3, 0.3))
	plt.title("Flux histogram : %s" % (src.name + " / " + deckey))
	plt.xlabel("Flux, in electrons")
	
	
	if savefigs:
		plotfilepath = os.path.join(plotdir, "%s_check_fluxhist_%s.pdf" % (figbase, src.name))
		plt.savefig(plotfilepath)
		print "Wrote %s" % (plotfilepath)
	else:
		plt.show()




	# Lightcurve
	
	plt.figure(figsize=(15, 8))
	
	decfilenums = np.array(map(int, [image[deckeyfilenum] for image in images]))
	
	(xmi, xma) = (np.min(decfilenums), np.max(decfilenums))
	(ymi, yma) = (np.min(normfluxes) - 0.5*np.std(normfluxes), np.max(normfluxes) + 0.5*np.std(normfluxes))
	
	#plt.axvline(mi, ymin=0.1, color="red")
	#plt.axvline(ma, ymin=0.1,color="red")
	#plt.figtext(0.15, 0.85, highflux)
	#plt.figtext(0.15, 0.83, lowflux)
	#plt.hist(fluxes, bins=200, color=(0.6, 0.6, 0.6))
	#plt.hist(normfluxes, bins=200, color=(0.3, 0.3, 0.3))
	plt.plot(decfilenums, normfluxes, marker=".", linestyle="none")
	plt.title("Lightcurve : %s" % (src.name + " / " + deckey))
	plt.xlabel("MCS files")
	plt.ylabel("Normalized flux")
	plt.xlim((xmi - 10.0, xma + 10.0))
	plt.ylim((ymi, yma))
	
	
	
	if savefigs:
		plotfilepath = os.path.join(plotdir, "%s_check_fluxlc_%s.pdf" % (figbase, src.name))
		plt.savefig(plotfilepath)
		print "Wrote %s" % (plotfilepath)
	else:
		plt.show()

	

	




