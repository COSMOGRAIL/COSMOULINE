"""
Joins images by night, automatically splitting according to different telescope names, 
and exports the resulting lightcurves as plain rdb lists.
"""

execfile("config.py")
import matplotlib.pyplot as plt
import matplotlib.dates


# Reading the db :
images = variousfct.readpickle(dbfilepath, verbose=True)
print "%i images in db." % (len(images))

# Selecting the right telescopes and setnames :
images = [image for image in images if (image["telescopename"] in telescopenames) and (image["setname"] in setnames)]
print "%i images have the choosen telescope- and set- names." % (len(images))

# Selecting the right deconvolution :
images = [image for image in images if image["decfilenum_" + deconvname] != None] 
print "%i images are deconvolved (among the latter)." % (len(images))

# Rejecting bad images :
print "Selection input      : %i" % (len(images))
images = [image for image in images if image["seeing"] <= imgmaxseeing]
print "Selecting seeing     : %i" % (len(images))
images = [image for image in images if image["ell"] <= imgmaxell]
print "Selecting ell        : %i" % (len(images))
images = [image for image in images if image["skylevel"] <= imgmaxskylevel]
print "Selecting skylevel   : %i" % (len(images))
images = [image for image in images if image["medcoeff"] <= imgmaxmedcoeff]
print "Selecting medcoeff   : %i" % (len(images))

# Rejecting according to an eventual skiplist :
if imgskiplistfilename != None:
	imgskiplist = variousfct.readimagelist(os.path.join(lcmanipdir, imgskiplistfilename))
	# Getting the image names, disregarding the comments :
	imgskiplist = [item[0] for item in imgskiplist]
	images = [image for image in images if image["imgname"] not in imgskiplist]

print "Selection output     : %i" % (len(images))


# Ok, the selection is done, we are left with the good images.

# Grouping them by nights :
nights = groupfct.groupbynights(images, separatesetnames=False)
print "This gives me %i nights." % len(nights)

nbimgs = map(len, nights) # The number of images in each night

print "Histogram of night lengths :"
h = ["%2i images : %4i nights" % (c, nbimgs.count(c)) for c in sorted(list(set(nbimgs)))]
for l in h:
	print l



# Calculating mean/median of values common to all sources within the nights.
# They are stored as lists or numpy arrays, and will be written as columns into the rdb file.

mhjds = groupfct.values(nights, 'mhjd', normkey=None)['mean']

medairmasses = groupfct.values(nights, 'airmass', normkey=None)['median']
medseeings = groupfct.values(nights, 'seeing', normkey=None)['median']
medells = groupfct.values(nights, 'ell', normkey=None)['median']
medskylevels = groupfct.values(nights, 'skylevel', normkey=None)['median']
mednormcoeffs = groupfct.values(nights, normcoeffname, normkey=None)['median'] # Normalization coeff to apply to the fluxes
meannormcoefferrs = np.fabs(np.array(groupfct.values(nights, normcoeffname+"_err", normkey=None)['mean'])) # Absolute error on these coeffs
#mednormcoefferrs = np.fabs(np.array(groupfct.values(nights, normcoeffname+"_err", normkey=None)['median'])) # Absolute error on these coeffs
# i.e., this is the mean of the stddev between the stars in each image.

meanrelcoefferrs = meannormcoefferrs / mednormcoeffs # relative errors on the norm coeffs
#medrelcoefferrs = mednormcoefferrs / mednormcoeffs # relative errors on the norm coeffs


meannormcoeffnbs = np.fabs(np.array(groupfct.values(nights, normcoeffname+"_comment", normkey=None)['mean'])) # Number of stars for coeff (mean -> float !)
print "Histogram of mean number of stars per coeff :"
h = ["%2i stars : %4i nights" % (c, list(meannormcoeffnbs).count(c)) for c in sorted(list(set(list(meannormcoeffnbs))))]
for l in h:
	print l





medrelskylevels = np.asarray(medskylevels)*np.asarray(mednormcoeffs)

meddates = [variousfct.DateFromJulianDay(mhjd + 2400000.5).strftime("%Y-%m-%dT%H:%M:%S") for mhjd in mhjds]

telescopenames = ["+".join(sorted(set([img["telescopename"] for img in night]))) for night in nights]
setnames = ["+".join(sorted(set([img["setname"] for img in night]))) for night in nights]



# The flags for nights (True if the night is OK) :
nightseeingbad = np.asarray(medseeings) < nightmaxseeing
nightellbad = np.asarray(medells) < nightmaxell
nightskylevelbad = medrelskylevels < nightmaxskylevel
nightnormcoeffbad = np.asarray(mednormcoeffs) < nightmaxnormcoeff
nightnbimgbad = np.asarray(nbimgs) >= nightminnbimg

flags = np.logical_and(np.logical_and(nightseeingbad, nightellbad), np.logical_and(nightskylevelbad, nightnormcoeffbad))
flags = np.logical_and(flags, nightnbimgbad)
print "%i nights are flagged as bad (i.e., they have flag = False)." % (np.sum(flags == False))


# We prepare a structure for the rdb file. It is an ordered list of dicts, each dict has two keys : column name and the data.

exportcols = [
{"name":"mhjd", "data":mhjds},
{"name":"datetime", "data":meddates},
{"name":"telescope", "data":telescopenames},
{"name":"setname", "data":setnames},
{"name":"nbimg", "data":nbimgs},
{"name":"fwhm", "data":medseeings},
{"name":"airmass", "data":medairmasses},
{"name":"relskylevel", "data":medrelskylevels},
{"name":"normcoeff", "data":mednormcoeffs},
{"name":"flag", "data":flags}
]


# Calculating median mags and errors for the sources (same idea, once for every source) :

for i, sourcename in enumerate(sourcenames):
	
	fluxfieldname = "out_%s_%s_flux" % (deconvname, sourcename)
	shotnoisefieldname = "out_%s_%s_shotnoise" % (deconvname, sourcename)
	
	normfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['median'])
	normshotnoises = np.fabs(np.array(groupfct.values(nights, shotnoisefieldname, normkey=normcoeffname)['median']))
	
	# We have already calculated the relative coeff errors. Turning them into absolute ones :
	normnormcoefferrs = normfluxes * meanrelcoefferrs
	
	# And combining the two error sources :
	normfluxerrorbars = np.sqrt(normnormcoefferrs**2 + normshotnoises**2)
	
	if not np.all(normfluxes > 0.0):
		raise RuntimeError("Negative Fluxes  !")
	
	mags = -2.5 * np.log10(normfluxes)
	magerrs = 2.5 * np.log10(np.asarray(1.0 + normfluxerrorbars/normfluxes))
	
	# We add these to the above structure for the rdb file :
	exportcols.extend([{"name":"mag_%s" % sourcename, "data":mags}, {"name":"magerr_%s" % sourcename, "data":magerrs}])


# Done with all calculations, now we export this to an rdb file...


rdbexport.writerdb(exportcols, os.path.join(lcmanipdir, outputname + ".rdb"), True)


# And make a plot just for the fun of it.

plt.figure(figsize=(20,12))
for i, sourcename in enumerate(sourcenames):
	mags = [col for col in exportcols if col["name"] == "mag_%s" % sourcename][0]["data"]
	magerrs = [col for col in exportcols if col["name"] == "magerr_%s" % sourcename][0]["data"]
	
	plt.errorbar(mhjds, mags, yerr=magerrs, linestyle="None", marker=".", label = sourcename)
	# Circles around flagged points :

	plt.plot(np.asarray(mhjds)[flags == False], np.asarray(mags)[flags == False], linestyle="None", marker="o", markersize=8., markeredgecolor="black", markerfacecolor="None", color="black")
		

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds), np.max(mhjds)) # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

#plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

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


if showplots == True:
	plt.show()
	print "Done."
else:
	plt.savefig(os.path.join(lcmanipdir, outputname + "_plot.pdf"))
	print "Wrote plot, done."


