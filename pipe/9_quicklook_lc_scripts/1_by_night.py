"""
Very similar to 0_mag_hjd.py, but we group the points per night.
"""


execfile("../config.py")
from kirbybase import KirbyBase, KBError
import combibynight_fct
import headerstuff
import star
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import rdbexport

print "You want to analyze the deconvolution %s" %deckey
print "Deconvolved object : %s" % decobjname
print "I will use the normalization coeffs used for the deconvolution."

ptsources = star.readmancat(ptsrccat)
print "Number of point sources : %i" % len(ptsources)
print "Names of sources : %s" % ", ".join([s.name for s in ptsources])


db = KirbyBase()

images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])
print "%i images" % len(images)

groupedimages = combibynight_fct.groupbynights(images)
print "%i nights"% len(groupedimages)

fieldnames = db.getFieldNames(imgdb)

plt.figure(figsize=(15,8))

mhjds = combibynight_fct.values(groupedimages, 'mhjd', normkey=None)['mean']

"""
medairmasses = combibynight_fct.values(groupedimages, 'airmass', normkey=None)['median']
medseeings = combibynight_fct.values(groupedimages, 'seeing', normkey=None)['median']
medskylevels = combibynight_fct.values(groupedimages, 'skylevel', normkey=None)['median']
meddeccoeffs = combibynight_fct.values(groupedimages, deckeynormused, normkey=None)['median']

meddates = [headerstuff.DateFromJulianDay(mhjd + 2400000.5).strftime("%Y-%m-%dT%H:%M:%S") for mhjd in mhjds]

telescopenames = [night[0]["telescopename"] for night in groupedimages]
setnames = [night[0]["setname"] for night in groupedimages]
"""

"""
exportcols = [
{"name":"mhjd", "data":mhjds},
{"name":"datetime", "data":meddates},
{"name":"telescope", "data":telescopenames},
{"name":"setname", "data":setnames},
{"name":"fwhm", "data":medseeings},
{"name":"airmass", "data":medairmasses},
{"name":"skylevel", "data":medskylevels},
{"name":"deccoeff", "data":meddeccoeffs}
]
"""

#deckeynormused = "medcoeff"

#colors = ["red", "blue", "purple", "green"]
for j, s in enumerate(ptsources):

	
	fluxfieldname = "out_%s_%s_flux" % (deckey, s.name)
	randomerrorfieldname = "out_%s_%s_shotnoise" % (deckey, s.name)
	
	mags = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused)['median']
	#errors = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused)['median']
	
	
	absfluxerrors = np.array(combibynight_fct.values(groupedimages, randomerrorfieldname, normkey=deckeynormused)['median'])
	fluxvals = np.array(combibynight_fct.values(groupedimages, fluxfieldname, normkey=deckeynormused)['median'])
	
	#relfluxerrors = absfluxerrors / fluxvals
	#magerrorbars = -2.5*np.log10(relfluxerrors)
	
	#print magerrorbars
	
	upmags = -2.5*np.log10(fluxvals + absfluxerrors)
	downmags = -2.5*np.log10(fluxvals - absfluxerrors)
	magerrorbars = (downmags - upmags) / 2.0
	
	plt.errorbar(mhjds, mags, yerr=[upmags-mags, mags-downmags], linestyle="None", marker=".", label = s.name)
	
	#exportcols.extend([{"name":"mag_%s" % ptsrc.name, "data":mags}, {"name":"magerr_%s" % ptsrc.name, "data":2.0*magerrorbars}])
	

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds), np.max(mhjds)) # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

#plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

titletext1 = "%s (%i nights)" % (xephemlens.split(",")[0], len(groupedimages))
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
	plt.savefig(os.path.join(plotdir, "%s_by_night.pdf" % deckey))
else:
	plt.show()


#for el in exportcols:
#	print len(el["data"])

#rdbexport.writerdb(exportcols, "out.rdb", True)

