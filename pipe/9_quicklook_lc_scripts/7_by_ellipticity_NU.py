"""
We color points according to ellipticity.
"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
import variousfct
import headerstuff
import star
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates


print "You want to analyze the deconvolution %s" %deckey
print "Deconvolved object : %s" % decobjname
if plotnormfieldname == None:
	print "I will use the normalization coeffs used for the deconvolution."
else:
	print "Using %s for the normalization." % (plotnormfieldname)
	deckeynormused = plotnormfieldname

ptsources = star.readmancat(ptsrccat)
print "Number of point sources : %i" % len(ptsources)
print "Names of sources : %s" % ", ".join([s.name for s in ptsources])

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])
print "%i images" % len(images)

fieldnames = db.getFieldNames(imgdb)

plt.figure(figsize=(15,15))

mhjds = np.array([image["mhjd"] for image in images])
ells = np.array([image["ell"] for image in images])

for s in ptsources:

	fluxfieldname = "out_%s_%s_flux" % (deckey, s.name)
	
	mags = -2.5*np.log10(np.array([image[fluxfieldname]*image[deckeynormused] for image in images]))
	
	plt.scatter(mhjds, mags, s=12, c=ells, vmin=0.01,vmax=0.3, edgecolors='none')

plt.grid(True)

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds), np.max(mhjds)) # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

#plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

titletext1 = "%s (%i points)" % (xephemlens.split(",")[0], len(images))
titletext2 = deckey

ax.text(0.02, 0.97, titletext1, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)
ax.text(0.02, 0.94, titletext2, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)


if plotnormfieldname:
	titletext3 = "Renormalized with %s" % (plotnormfieldname)
	ax.text(0.02, 0.91, titletext3, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)

cbar = plt.colorbar(orientation='horizontal')
cbar.set_label('Ellipticity') 

# Second x-axis with actual dates :
yearx = ax.twiny()
yearxmin = headerstuff.DateFromJulianDay(np.min(mhjds) + 2400000.5)
yearxmax = headerstuff.DateFromJulianDay(np.max(mhjds) + 2400000.5)
yearx.set_xlim(yearxmin, yearxmax)
yearx.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
yearx.xaxis.set_major_locator(matplotlib.dates.YearLocator())
yearx.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
yearx.xaxis.tick_top()
yearx.set_xlabel("Date")

if savefigs:
	if plotnormfieldname:
		plotfilepath = os.path.join(plotdir, "%s_lc_%s_by_ellipticity.pdf" % (deckey, plotnormfieldname))
	else :
		plotfilepath = os.path.join(plotdir, "%s_lc_by_ellipticity.pdf" % (deckey))
	plt.savefig(plotfilepath)
	print "Wrote %s" % (plotfilepath)
else:
	plt.show()

