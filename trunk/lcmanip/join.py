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
print "%i images have the chosen telescope- and set- names." % (len(images))

# Selecting the right deconvolution :
images = [image for image in images if image["decfilenum_" + deconvname] != None] 
print "%i images are deconvolved (among the latter)." % (len(images))
ava = len(images)

# Special tweak if you request medcoeff ...
if normcoeffname == "medcoeff":
	# We just want to avoid that it crashes...
	for image in images:
		image["medcoeff_err"] = 0.0
		image["medcoeff_comment"] = "0"



# Rejecting bad images :

before = len(images)
images = [image for image in images if image["seeing"] <= imgmaxseeing]
print "Rejected because seeing > %.2f : %i" % (imgmaxseeing, before-len(images))

before = len(images)
images = [image for image in images if image["ell"] <= imgmaxell]
print "Rejected because ell > %.2f : %i" % (imgmaxell, before-len(images))

before = len(images)
images = [image for image in images if image["skylevel"]*image["medcoeff"] <= imgmaxrelskylevel] # We rescale the sky level in the same way as for source fluxes.
print "Rejected because relskylevel > %.2f : %i" % (imgmaxrelskylevel, before-len(images))

before = len(images)
images = [image for image in images if image["medcoeff"] <= imgmaxmedcoeff]
print "Rejected because medcoeff > %.2f : %i" % (imgmaxmedcoeff, before-len(images))

# Rejecting according to an eventual skiplist :
if imgskiplistfilename != None:
	imgskiplist = variousfct.readimagelist(os.path.join(lcmanipdir, imgskiplistfilename))
	# Getting the image names, disregarding the comments :
	imgskiplist = [item[0] for item in imgskiplist]
	images = [image for image in images if image["imgname"] not in imgskiplist]

print "Number of rejected images : %i." % (ava - len(images))
print "We keep %i images among %i." % (len(images), ava)

# Ok, the selection is done, we are left with the good images.

# Checking for negative fluxes, before combining by nights.
# We do not crash, just print out info to write on skiplist ...
for image in images:
	for sourcename in sourcenames:
		fluxfieldname = "out_%s_%s_flux" % (deconvname, sourcename)
		
		try:
			if float(image[fluxfieldname]) < 0.0:
				print "%s ERROR, negative flux for source %s" % (image["imgname"], sourcename)
				#print "Please, put this image on a skiplist."
		except:
			print "%s ERROR, not a float : %s" % (image["imgname"], image[fluxfieldname])
		
		try:
			if float(image[normcoeffname]) < 0.0:
				print "%s ERROR, negative normcoeff for source %s" % (image["imgname"], sourcename)
				#print "Please, put this image on a skiplist."
		except:
			print "%s ERROR, not a float : %s" % (image["imgname"], image[normcoeffname])

# Combining shotnoise and renormerror per image and adding this to the database (needed for Error3)
# Error on f(x*y) = sqrt(x**2 * y_err**2 + y**2 * x_err**2)
# Correcting the renormcoefferr by dividing it by the number of renormstars

for image in images:
	for sourcename in sourcenames:
	
		fluxfieldname = "out_%s_%s_flux" % (deconvname, sourcename)
		shotnoisefieldname = "out_%s_%s_shotnoise" % (deconvname, sourcename)
		
		image[normcoeffname+"_err"] = image[normcoeffname+"_err"] / float(image[normcoeffname+"_comment"])
		combierror = np.sqrt((image[normcoeffname]**2 * image[shotnoisefieldname]**2) + (image[fluxfieldname]**2 * image[normcoeffname+"_err"]**2))
		image["out_" + deconvname + "_" + sourcename + "_combierr"] = combierror

# Grouping them by nights :
nights = groupfct.groupbynights(images, separatesetnames=False)
print "This gives me %i nights." % len(nights)

nbimgs = map(len, nights) # The number of images in each night

print "Histogram of number of images per night :"
h = ["%4i nights with %i images" % (nbimgs.count(c), c) for c in sorted(list(set(nbimgs)))]
for l in h:
	print l



# Calculating mean/median of values common to all sources within the nights.
# They are stored as lists or numpy arrays, and will be written as columns into the rdb file.

mhjds = groupfct.values(nights, 'mhjd', normkey=None)['mean']
meddates = [variousfct.DateFromJulianDay(mhjd + 2400000.5).strftime("%Y-%m-%dT%H:%M:%S") for mhjd in mhjds]
telescopenames = ["+".join(sorted(set([img["telescopename"] for img in night]))) for night in nights]
setnames = ["+".join(sorted(set([img["setname"] for img in night]))) for night in nights]

medairmasses = groupfct.values(nights, 'airmass', normkey=None)['median']
medseeings = groupfct.values(nights, 'seeing', normkey=None)['median']
medells = groupfct.values(nights, 'ell', normkey=None)['median']
medskylevels = groupfct.values(nights, 'skylevel', normkey=None)['median']
mednormcoeffs = groupfct.values(nights, normcoeffname, normkey=None)['median']
medrelskylevels = np.asarray(medskylevels)*np.asarray(mednormcoeffs) # We rescale the sky level in the same way as for source fluxes.

# Some calculations about the normalization and its errors

#meannormcoefferrs = np.fabs(np.array(groupfct.values(nights, normcoeffname+"_err", normkey=None)['mean'])) # Absolute error on these coeffs
mednormcoefferrs = np.fabs(np.array(groupfct.values(nights, normcoeffname+"_err", normkey=None)['median'])) # Absolute error on these coeffs
# i.e., this is the med of the stddev between the stars in each image.

if min(mednormcoefferrs) <= 0.0001:
	print "####### WARNING : some normcoefferrs seem to be zero ! #############"
	print "Check/redo the normalization, otherwise some of my error bars might be too small."
	

#meanrelcoefferrs = meannormcoefferrs / mednormcoeffs # relative errors on the norm coeffs
medrelcoefferrs = mednormcoefferrs / mednormcoeffs # relative errors on the norm coeffs

meannormcoeffnbs = np.fabs(np.array(groupfct.values(nights, normcoeffname+"_comment", normkey=None)['mean'])) # Number of stars for coeff (mean -> float !)
print "Histogram of mean number of normalization stars per night :"
h = ["%4i nights with %i stars" % (list(meannormcoeffnbs).count(c), c) for c in sorted(list(set(list(meannormcoeffnbs))))]
for l in h:
	print l


# The flags for nights (True if the night is OK) :
nightseeingbad = np.asarray(medseeings) < nightmaxseeing
print "Night seeing > %.2f : %i" % (nightmaxseeing, np.sum(nightseeingbad == False))
nightellbad = np.asarray(medells) < nightmaxell
print "Night ell > %.2f : %i" % (nightmaxell, np.sum(nightellbad == False))
nightskylevelbad = medrelskylevels < nightmaxrelskylevel
print "Night relskylevel > %.2f : %i" % (nightmaxrelskylevel, np.sum(nightskylevelbad == False))
nightnormcoeffbad = np.asarray(mednormcoeffs) < nightmaxnormcoeff
print "Night normcoeff > %.2f : %i" % (nightmaxnormcoeff, np.sum(nightnormcoeffbad == False))
nightnbimgbad = np.asarray(nbimgs) >= nightminnbimg
print "Night nbimg < %i : %i" % (nightminnbimg, np.sum(nightnbimgbad == False))

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
{"name":"elongation", "data":medells},
{"name":"airmass", "data":medairmasses},
{"name":"relskylevel", "data":medrelskylevels},
{"name":"normcoeff", "data":mednormcoeffs},
{"name":"flag", "data":flags}
]


# Calculating median mags and errors for the sources (same idea, once for every source) :

for i, sourcename in enumerate(sourcenames):
	
	fluxfieldname = "out_%s_%s_flux" % (deconvname, sourcename)
	shotnoisefieldname = "out_%s_%s_shotnoise" % (deconvname, sourcename)
	combierrorfieldname = "out_%s_%s_combierr" % (deconvname, sourcename)
	
	# Getting the normalized median fluxes, and converting them to mags :
	normfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['median'])
	if not np.all(normfluxes > 0.0):
		raise RuntimeError("Negative Fluxes  !")
	mags = -2.5 * np.log10(normfluxes)
	
	##### Errorbar 0 : shotnoise error of a typicial individual image in this night divided by the sqrt of the number of images within the night
	normshotnoises = np.fabs(np.array(groupfct.values(nights, shotnoisefieldname, normkey=normcoeffname)['median']))
	normshotnoises = normshotnoises / np.sqrt(nbimgs)
	magerrs0 = 2.5 * np.log10(1.0 + normshotnoises/normfluxes)
	
	
	##### Errorbar 1 : Old formula: shotnoise combined with renormalization error of a typical image in this night.
	# We have already calculated the relative coeff errors. Turning them into absolute ones and combining with shotnoise :
	normnormcoefferrs = normfluxes * medrelcoefferrs
	normcombierrors = np.sqrt(normnormcoefferrs**2 + normshotnoises**2)
	magerrs1 = 2.5 * np.log10(1.0 + normcombierrors/normfluxes)
	
	##### Errorbar 2 : New formula but still with median shotnoise combined with median renormalization error of a typical image in this night.
	# combined error of flux*normcoeff = sqrt(normcoeff**2 * shotnoise**2 + flux**2 * normcoefferr**2):
	medfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=None)['median'])
	medshotnoises = np.fabs(np.array(groupfct.values(nights, shotnoisefieldname, normkey=None)['median']))
	medshotnoises = medshotnoises / np.sqrt(nbimgs)
	medcombierrors = np.sqrt((np.asarray(mednormcoeffs)**2 * medshotnoises**2) + (medfluxes**2 * mednormcoefferrs**2))
	magerrs2 = 2.5 * np.log10(1.0 + medcombierrors/normfluxes)
	
	##### Errorbar 3 : New formula with median of combined error per image of shotnoise and renormerr, divided by the number of images per night
	combinighterrors = np.fabs(np.array(groupfct.values(nights, combierrorfieldname, normkey=normcoeffname)['median']))
	combinighterrors = combinighterrors / np.sqrt(nbimgs)
	magerrs3 = 2.5 * np.log10(1.0 + combinighterrors/normfluxes)
	
	##### Errorbar 4 : MAD estimator of the spread of photometric measurements within this night,
	# scaled by a factor assuming a gaussian distribution.
	# http://en.wikipedia.org/wiki/Median_absolute_deviation
	# Nights with less than 3 images get 3 times the median error.
	normmads = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['mad'])
	normmads = normmads / np.sqrt(nbimgs)
	normmads *= 1.4826
	magerrs4 = 2.5 * np.log10(1.0 + normmads/normfluxes)
	magerrs4[np.array(nbimgs) < 3] = 3.0 * np.median(magerrs4)
	
	##### Errorbar 5 : maximum of theoretical and pragmatic errorbar
	magerrs_temp = np.maximum(magerrs1,magerrs2)
	magerrs5 = np.maximum(magerrs_temp,magerrs4)
	
	"""
	##### Errorbar 6 : max-to-min spread of photometric measurements within this night (recentered = symmetric error bar)
	# Nights with less than 3 images get 3 times the median error.
	maxnormfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['max'])
	minnormfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['min'])
	normfluxspreads = maxnormfluxes - minnormfluxes
	magerrs6 = 2.5 * np.log10(1.0 + normfluxspreads/normfluxes)
	magerrs6[np.array(nbimgs) < 3] = 3.0 * np.median(magerrs3)
	"""

	
	# We add these to the above structure for the rdb file :
	exportcols.append({"name":"mag_%s" % sourcename, "data":mags})
	exportcols.append({"name":"magerr_%s_0" % sourcename, "data":magerrs0})
	exportcols.append({"name":"magerr_%s_1" % sourcename, "data":magerrs1})
	exportcols.append({"name":"magerr_%s_2" % sourcename, "data":magerrs2})
	exportcols.append({"name":"magerr_%s_3" % sourcename, "data":magerrs3})
	exportcols.append({"name":"magerr_%s_4" % sourcename, "data":magerrs4})
	exportcols.append({"name":"magerr_%s_5" % sourcename, "data":magerrs5})
	#exportcols.append({"name":"magerr_%s_6" % sourcename, "data":magerrs6})

	#print "Source %s" % (sourcename)
	#print "Median flux [electrons]      : %.2f" % (np.median(normfluxes))
	#print "Median shotnoise [electrons] : %.2f" % (np.median(normshotnoises))
	#print "Median normerror [electrons] : %.2f" % (np.median(normnormcoefferrs))
	#print "Min normerror [electrons]    : %.2f" % (np.min(normnormcoefferrs))
	#print "Max normerror [electrons]    : %.2f" % (np.max(normnormcoefferrs))


# Done with all calculations, now we export this to an rdb file...
rdbexport.writerdb(exportcols, os.path.join(lcmanipdir, outputname + ".rdb"), writeheader=writeheader)


# And make a plot just for the fun of it.
plt.figure(figsize=(20,12))
for i, sourcename in enumerate(sourcenames):
	mags = [col for col in exportcols if col["name"] == "mag_%s" % sourcename][0]["data"]
	magerrs = [col for col in exportcols if col["name"] == "magerr_%s_4" % sourcename][0]["data"]
	
	plt.errorbar(mhjds, mags, yerr=magerrs, linestyle="None", marker=".", label = sourcename)
	# Circles around flagged points :

	plt.plot(np.asarray(mhjds)[flags == False], np.asarray(mags)[flags == False], linestyle="None", marker="o", markersize=8., markeredgecolor="black", markerfacecolor="None", color="black")
		

# reverse y axis for magnitudes :
ax=plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds)-100.0, np.max(mhjds)+100.0) # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

#plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

plt.legend()
#leg = ax.legend(loc='upper right', fancybox=True)
#leg.get_frame().set_alpha(0.5)
leg = ax.legend(loc='lower right')
#leg.get_frame().set_alpha(0.5)

# Second x-axis with actual dates :
yearx = ax.twiny()
yearxmin = variousfct.DateFromJulianDay(np.min(mhjds) + 2400000.5 - 100.0)
yearxmax = variousfct.DateFromJulianDay(np.max(mhjds) + 2400000.5 + 100.0)
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


