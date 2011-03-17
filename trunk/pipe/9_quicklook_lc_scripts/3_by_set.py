"""
Again very similar, but different colours for different setnames
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
print "I will use the normalization coeffs used for the deconvolution."

ptsources = star.readmancat(ptsrccat)
print "Number of point sources : %i" % len(ptsources)
print "Names of sources : %s" % ", ".join([s.name for s in ptsources])

db = KirbyBase()
allimages = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])
print "%i images" % len(allimages)

fieldnames = db.getFieldNames(imgdb)
setnames = sorted(list(set([image["setname"] for image in allimages])))

plt.figure(figsize=(15,15))

for setname in setnames:

	print setname
	images = [image for image in allimages if image["setname"] == setname]
	
	magarraylist = []
	mhjdarraylist = []

	for s in ptsources:

		fluxfieldname = "out_%s_%s_flux" % (deckey, s.name)
		
		mhjds = np.array([image["mhjd"] for image in images])
		mags = -2.5*np.log10(np.array([image[fluxfieldname]*image[deckeynormused] for image in images]))
	
		magarraylist.append(mags)
		mhjdarraylist.append(mhjds)

	mags = np.concatenate(magarraylist)
	mhjds = np.concatenate(mhjdarraylist)

	plt.plot(mhjds, mags, linestyle="None", marker=".", label = "Set %s (%i points)" % (setname, len(images)))

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


#plt.legend()
leg = ax.legend(loc='upper right', fancybox=True)
leg.get_frame().set_alpha(0.5)

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
	plotfilepath = os.path.join(plotdir, "%s_lc_by_sets.pdf" % deckey)
	plt.savefig(plotfilepath)
	print "Wrote %s" % (plotfilepath)
else:
	plt.show()


