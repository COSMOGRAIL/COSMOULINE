"""
Mag vs. MJD
Relies on info in settings.py
Does not bin the measurements by nights.
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
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])
print "%i images" % len(images)

fieldnames = db.getFieldNames(imgdb)

plt.figure(figsize=(15,8))

mhjds = np.array([image["mhjd"] for image in images])

for s in ptsources:

	fluxfieldname = "out_%s_%s_flux" % (deckey, s.name)
	randomerrorfieldname = "out_%s_%s_shotnoise" % (deckey, s.name)
	
	mags = -2.5*np.log10(np.array([image[fluxfieldname]*image[deckeynormused] for image in images]))
	
	if randomerrorfieldname not in fieldnames :
		plt.plot(mhjds, mags, linestyle="None", marker=".", label = s.name)
	else :
		upmags =   -2.5*np.log10(np.array([(image[fluxfieldname] - image[randomerrorfieldname])*image[deckeynormused] for image in images]))
		downmags = -2.5*np.log10(np.array([(image[fluxfieldname] + image[randomerrorfieldname])*image[deckeynormused] for image in images]))

		plt.errorbar(mhjds, mags, yerr=[upmags-mags, mags-downmags], linestyle="None", marker=".", label = s.name)
	plt.errorbar

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
ax.text(0.02, 0.93, titletext2, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)


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
	plt.savefig(os.path.join(plotdir, "%s_mag_hdj.pdf" % deckey))
else:
	plt.show()

	
