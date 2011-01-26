execfile("../config.py")
from kirbybase import KirbyBase, KBError
import combibynight_fct
import headerstuff
import star
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import rdbexport


print "Deconvolution %s" %deckey

ptsrcs = star.readmancat(ptsrccat)
print "Point sources : %s" % ",".join([ptsrc.name for ptsrc in ptsrcs])


db = KirbyBase()
# the \d\d* is a trick to select both 0000-like and 000-like
images = db.select(imgdb, [deckeyfilenum], ['\d\d*'], returnType='dict', useRegExp=True, sortFields=['mjd'])
print "%i images" % len(images)
groupedimages = combibynight_fct.groupbynights(images)
print "%i nights"% len(groupedimages)
fieldnames = db.getFieldNames(imgdb)

plt.figure(figsize=(12,8))

mhjds = combibynight_fct.values(groupedimages, 'mhjd', normkey=None)['median']

medairmasses = combibynight_fct.values(groupedimages, 'airmass', normkey=None)['median']
medseeings = combibynight_fct.values(groupedimages, 'seeing', normkey=None)['median']
medskylevels = combibynight_fct.values(groupedimages, 'skylevel', normkey=None)['median']
meddeccoeffs = combibynight_fct.values(groupedimages, deckeynormused, normkey=None)['median']

meddates = [headerstuff.DateFromJulianDay(mhjd + 2400000.5).strftime("%Y-%m-%dT%H:%M:%S") for mhjd in mhjds]

exportcols = [
{"name":"mhjd", "data":mhjds},
{"name":"datetime", "data":meddates},
{"name":"fwhm", "data":medseeings},
{"name":"airmass", "data":medairmasses},
{"name":"skylevel", "data":medskylevels},
{"name":"deccoeff", "data":meddeccoeffs},
]


colors = ["red", "blue", "purple", "green"]
for j, ptsrc in enumerate(ptsrcs):

	
	fluxfieldname = "out_%s_%s_flux" % (deckey, ptsrc.name)
	
	mags = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused)['median']
	#errors = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused)['median']
	
	
	randomerrorfieldname = "out_%s_%s_randerror" % (deckey, ptsrc.name)
	
	
	absfluxerrors = np.array(combibynight_fct.values(groupedimages, randomerrorfieldname, normkey=deckeynormused)['median'])
	fluxvals = np.array(combibynight_fct.values(groupedimages, fluxfieldname, normkey=deckeynormused)['median'])
	relfluxerrors = absfluxerrors / fluxvals
	
	#magerrorbars = -2.5*np.log10(relfluxerrors)
	
	#print magerrorbars
	
	upmags = -2.5*np.log10(fluxvals + absfluxerrors)
	downmags = -2.5*np.log10(fluxvals - absfluxerrors)
	magerrorbars = (downmags - upmags) / 2.0
	#print magerrorbars
	
	plt.errorbar(mhjds, mags, yerr=2.0*magerrorbars, linestyle="None", marker=".", label = ptsrc.name)
	exportcols.extend([{"name":"mag_%s" % ptsrc.name, "data":mags}, {"name":"magerr_%s" % ptsrc.name, "data":2.0*magerrorbars}])
	
	#plt.plot(mhjds, mags, linestyle="None", marker=".", label = ptsrc.name)
	
	#mymagups = asarray(mags(groupedimages, 'out_'+deckey+'_'+ src.name +'_flux')['up'])
	#mymagdowns = asarray(mags(groupedimages, 'out_'+deckey+'_'+ src.name +'_flux')['down'])
	#mhjds = asarray(values(groupedimages, 'mhjd')['median'])
	
	#randomerrorfieldname = "out_%s_%s_randerror" % (deckey, ptsrc.name)
	
	#if randomerrorfieldname not in fieldnames :
	#	plt.plot(mhjds, mags, linestyle="None", marker=".", label = ptsrc.name)
	#else :
	#	upmags =   -2.5*np.log10(np.array([(image[fluxfieldname] - image[randomerrorfieldname])*image[deckeynormused] for image in images]))
	#	downmags = -2.5*np.log10(np.array([(image[fluxfieldname] + image[randomerrorfieldname])*image[deckeynormused] for image in images]))

	#plt.errorbar(mhjds, mags, yerr=[upmags-mags, mags-downmags], linestyle="None", marker=".", label = s.name)
	#plt.errorbar



# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds), np.max(mhjds)) # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

#plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

titletext = deckey
titletext = "%s (%i points)" % (xephemlens.split(",")[0], len(images))

plt.legend()
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


plt.show()

#for el in exportcols:
#	print len(el["data"])

rdbexport.writerdb(exportcols, "out.rdb", True)

