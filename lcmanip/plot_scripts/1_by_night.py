execfile("../config.py")

import matplotlib.pyplot as plt
import matplotlib.dates


print "Deconvolution : %s" % (deconvname)
print "Point sources : %s" % ", ".join(sourcenames)

images = variousfct.readpickle(pkldbpath, verbose=True)

images = [image for image in images if image["decfilenum_" + deconvname] != None] 
print "%i images" % len(images)

groupedimages = groupfct.groupbynights(images)
print "%i nights"% len(groupedimages)


plt.figure(figsize=(12,8))

mhjds = groupfct.values(groupedimages, 'mhjd', normkey=None)['mean']

medairmasses = groupfct.values(groupedimages, 'airmass', normkey=None)['median']
medseeings = groupfct.values(groupedimages, 'seeing', normkey=None)['median']
medskylevels = groupfct.values(groupedimages, 'skylevel', normkey=None)['median']
meddeccoeffs = groupfct.values(groupedimages, normcoeffname, normkey=None)['median']

medrelskylevels = np.array(medskylevels)*np.array(meddeccoeffs)

meddates = [variousfct.DateFromJulianDay(mhjd + 2400000.5).strftime("%Y-%m-%dT%H:%M:%S") for mhjd in mhjds]

telescopenames = [night[0]["telescopename"] for night in groupedimages]
setnames = [night[0]["setname"] for night in groupedimages]


exportcols = [
{"name":"mhjd", "data":mhjds},
{"name":"datetime", "data":meddates},
{"name":"telescope", "data":telescopenames},
{"name":"setname", "data":setnames},
{"name":"fwhm", "data":medseeings},
{"name":"airmass", "data":medairmasses},
{"name":"relskylevel", "data":medrelskylevels},
{"name":"normcoeff", "data":meddeccoeffs}
]
#{"name":"deccoeff", "data":meddeccoeffs}
#]

#deckeynormused = "medcoeff"


colors = ["red", "blue", "purple", "green"]
for i, sourcename in enumerate(sourcenames):

	
	fluxfieldname = "out_%s_%s_flux" % (deconvname, sourcename)
	
	#mags = groupfct.mags(groupedimages, fluxfieldname)['median']
	mags = groupfct.mags(groupedimages, fluxfieldname, normkey=normcoeffname)['median']
	
	#magerrors = 0.00 + (np.array(medskylevels)/200.0)*0.005 + (np.array(medseeings)/1.0)*0.005
	#errors = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=normcoeffname)['median']
	
	#plt.plot(mhjds, mags, linestyle="None", marker=".", label = sourcename, color = colors[i])
	#plt.errorbar(mhjds, mags, yerr=magerrors, linestyle="None", marker=".", label = sourcename, color = colors[i])
	
	
	randomerrorfieldname = "out_%s_%s_shotnoise" % (deconvname, sourcename)

	absfluxerrors = np.array(groupfct.values(groupedimages, randomerrorfieldname, normkey=normcoeffname)['max'])
	fluxvals = np.array(groupfct.values(groupedimages, fluxfieldname, normkey=normcoeffname)['median'])
	relfluxerrors = absfluxerrors / fluxvals
	
	##magerrorbars = -2.5*np.log10(relfluxerrors)
	
	##print magerrorbars
	
	upmags = -2.5*np.log10(fluxvals + absfluxerrors)
	downmags = -2.5*np.log10(fluxvals - absfluxerrors)
	magerrorbars = (downmags - upmags) / 2.0
	##print magerrorbars
	
	magerrorbars = magerrorbars * 2.0
	
	plt.errorbar(mhjds, mags, yerr=magerrorbars, linestyle="None", marker=".", label = sourcename)
	exportcols.extend([{"name":"mag_%s" % sourcename, "data":mags}, {"name":"magerr_%s" % sourcename, "data":magerrorbars}])
	
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

#titletext = deckey
#titletext = "%s (%i points)" % (xephemlens.split(",")[0], len(images))

plt.legend()
leg = ax.legend(loc='upper right', fancybox=True)
leg.get_frame().set_alpha(0.5)

# Second x-axis with actual dates :
yearx = ax.twiny()
yearxmin = variousfct.DateFromJulianDay(np.min(mhjds) + 2400000.5)
yearxmax = variousfct.DateFromJulianDay(np.max(mhjds) + 2400000.5)
yearx.set_xlim(yearxmin, yearxmax)
yearx.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
yearx.xaxis.set_major_locator(matplotlib.dates.YearLocator())
yearx.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
yearx.xaxis.tick_top()
yearx.set_xlabel("Date")

plt.show()





# we kick some bad images

#okflags = [True] * len(mhjds)

seeingflags = np.asarray(medseeings) < 2.1
skylevelflags = np.asarray(medrelskylevels) < 3500.0

okflags = np.logical_and(seeingflags, skylevelflags)
exportcols.append({"name":"flag", "data":okflags})


"""
for i, sourcename in enumerate(sourcenames):

	fluxfieldname = "out_%s_%s_flux" % (deconvname, sourcename)
	mags = groupfct.mags(groupedimages, fluxfieldname, normkey=normcoeffname)['median']
	
	plt.scatter(mhjds, mags, s=20, c=medrelskylevels, vmin=1000, vmax=5000, edgecolors=None)
	#plt.scatter(mhjds, mags, s=12, c=seeings, vmin=0.5,vmax=2.5, edgecolors='none')


cbar = plt.colorbar(orientation='horizontal')
cbar.set_label('FWHM [arcsec]') 

plt.show()
"""


#print seeingflags

#print okflags
#print len(okflags)
print "%i nights are OK" % (np.sum(okflags))



#for el in exportcols:
#	print len(el["data"])

rdbexport.writerdb(exportcols, "all.rdb", True)

