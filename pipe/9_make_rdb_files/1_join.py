"""
Joins images by night, automatically splitting according to different telescope names, 
and exports the resulting lightcurves as plain rdb lists.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')

from modules import variousfct, groupfct, rdbexport
from config import settings, configdir, pklfilepath


setnames = settings['exportsetnames']
telescopenames = settings['telescopenames']
deconvname = settings['deconvname']
normcoeffname = settings['normcoeffname']
imgmaxseeing = settings['imgmaxseeing']
imgmaxell = settings['imgmaxell']
imgmaxrelskylevel = settings['imgmaxrelskylevel']
imgmaxmedcoeff = settings['imgmaxmedcoeff']
imgskiplistfilename = settings['imgskiplistfilename']
nightmaxseeing = settings['nightmaxseeing']
sourcenames = settings['sourcenames']
outputname = settings['outputname']
nightmaxell = settings['nightmaxell']
nightmaxrelskylevel = settings['nightmaxrelskylevel']
nightmaxnormcoeff = settings['nightmaxnormcoeff']
nightminnbimg = settings['nightminnbimg']
writeheader = settings['writeheader']
showplots = settings['showplots']
renormname = settings['renormname']



# Reading the db :
images = variousfct.readpickle(pklfilepath, verbose=True)
print(f"{len(images)} images in db.")

# Selecting the right telescopes and setnames :
images = [image for image in images if ((image["telescopename"] in telescopenames)\
                                         and (image["setname"] in setnames) \
                                         and (image["gogogo"] == True)) ]
print(f"{len(images)} images have the chosen telescope- and set- names.")

# Selecting the right deconvolution :
images = [image for image in images if image["decfilenum_" + deconvname] != None] 
print(f"{len(images)} images are deconvolved (among the latter).")
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
print(f"Rejected because seeing > {imgmaxseeing:.2f} : {int(before - len(images))}")

before = len(images)
images = [image for image in images if image["ell"] <= imgmaxell]
print(f"Rejected because ell > {imgmaxell:.2f} : {int(before - len(images))}")

before = len(images)
images = [image for image in images if image["skylevel"]*image[renormname] <= imgmaxrelskylevel] # We rescale the sky level in the same way as for source fluxes.
print(f"Rejected because relskylevel > {imgmaxrelskylevel:.2f} : {int(before - len(images))}")


# Rejecting according to an eventual skiplist :
if imgskiplistfilename != None:
    if isinstance(imgskiplistfilename, list):
        for skip in imgskiplistfilename:
            imgskiplist = variousfct.readimagelist(os.path.join(configdir, skip))
            # Getting the image names, disregarding the comments :
            imgskiplist = [item[0] for item in imgskiplist]
            images = [image for image in images if image["imgname"] not in imgskiplist]
    else :
        imgskiplist = variousfct.readimagelist(os.path.join(configdir, imgskiplistfilename))
        # Getting the image names, disregarding the comments :
        imgskiplist = [item[0] for item in imgskiplist]
        images = [image for image in images if image["imgname"] not in imgskiplist]

print(f"Number of rejected images : {int(ava - len(images))}.")
print(f"We keep {len(images)} images among {int(ava)}.")

# Ok, the selection is done, we are left with the good images.

# Checking for negative fluxes and normalizations, before combining by nights.
# We do not crash, just print out info to write on skiplist ...
bad_index = []
for i, image in enumerate(images):
    for sourcename in sourcenames:
        fluxfieldname = f"out_{deconvname}_{sourcename}_flux"
        if float(image[fluxfieldname]) < 0.0:
            print(f"{image['imgname']} ERROR, negative flux for source {sourcename}")
            print("Please, put this image on a skiplist and re-export the database.")
            bad_index.append(i)

        # We also check the normalizations :
        if image[normcoeffname] is not None :
            if float(image[normcoeffname]) < 0.0:
                print(f"{image['imgname']} ERROR, negative normcoeff {normcoeffname}")
                bad_index.append(i)
        else :
            print(f"{image['imgname']} ERROR, none normcoeff {normcoeffname}")
            exit()

# We now add some new fields to each image, in preparation to the errorbar calculation.
print(f"I have {len(bad_index)} negative flux or negative normcoeff. I will remove those images.")
images = [image for i, image in enumerate(images) if i not in bad_index]
print(f"Number of rejected images : {int(ava - len(images))}.")
print(f"We keep {len(images)} images among {int(ava)}.")

for image in images:

    image[normcoeffname + "_sigma"] = image[normcoeffname + "_err"] 

    # - Combining shotnoise and renormsigma *per image*, in preparation for later calculations
    # Error on f(x*y) = sqrt(x**2 * y_err**2 + y**2 * x_err**2)
    # where : y = fluxfieldname +/- shotnoisefieldname
    #         x = normcoeffname +/- normcoeffname_sigma

    for sourcename in sourcenames:
        fluxfieldname = f"out_{deconvname}_{sourcename}_flux"
        shotnoisefieldname = f"out_{deconvname}_{sourcename}_shotnoise"

        combierror = np.sqrt((image[normcoeffname] ** 2 * image[shotnoisefieldname] ** 2) + (
                    image[fluxfieldname] ** 2 * image[normcoeffname + "_sigma"] ** 2))

        image["out_" + deconvname + "_" + sourcename + "_combierr"] = combierror

# At this point we group the images by nights, all the individual computations are done.

nights = groupfct.groupbynights(images, separatesetnames=False)
print(f"This gives me {len(nights)} nights.")

nbimgs = list(map(len, nights)) # The number of images in each night, as floats


print("Histogram of number of images per night :")
h = ["%4i nights with %i images" % (nbimgs.count(c), c) for c in sorted(list(set(nbimgs)))]
for l in h:
    print(l)


sqrtnbimgs = np.sqrt(np.array(nbimgs) + 0.0)  # This is the numpy array used for computations

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
mednormcoeffsigmas = np.fabs(np.array(
    groupfct.values(nights, normcoeffname + "_sigma", normkey=None)['median']))  # Absolute error on these coeffs
medrelnormcoeffsigmas = mednormcoeffsigmas / mednormcoeffs  # relative errors on the norm coeffs

import numpy as np
print("Median seeing: ", np.median([img["seeing"] for img in images]))
print("Median sampling: ", (np.max(mhjds)-np.min(mhjds))/len(nights))

fig1 = plt.figure(figsize=(6, 4))
fig1.subplots_adjust(left=0.1, right=0.97, bottom=0.15, top=0.98, wspace=0.01)
plt.subplot(1, 2, 1)
plt.hist(medseeings, bins=12, color="royalblue")
plt.axvline(np.median([img["seeing"] for img in images]), linestyle='--', color='grey', linewidth=2.0, alpha=0.5)
plt.annotate("$\mathrm{median = %.2f}$" % np.median([img["seeing"] for img in images]), xy=(0.31, 0.90),
             xycoords='axes fraction', xytext=(0, 0),
             textcoords='offset points', ha='left', va='bottom', fontsize=16)
plt.ylabel("$\mathrm{\# \ of \ nights}$", fontsize=18)
plt.xlabel("$\mathrm{seeing \ [arcsec]}$", fontsize=18)
# plt.axis([0.6, 2.4, 0, 30])

plt.subplot(1, 2, 2)
plt.hist(medairmasses, bins=12, color="crimson")
plt.axvline(np.median([img["airmass"] for img in images]), linestyle='--', color='grey', linewidth=2.0, alpha=0.5)
plt.annotate("$\mathrm{median = %.2f}$" % np.median([img["airmass"] for img in images]), xy=(0.31, 0.90),
             xycoords='axes fraction', xytext=(0, 0),
             textcoords='offset points', ha='left', va='bottom', fontsize=16)
plt.xlabel(r"$\mathrm{airmass}$", fontsize=18)
plt.yticks([])
# plt.axis([1.1, 1.6, 0, 30])
plt.show()
fig1.savefig(os.path.join(configdir, outputname + "_median_seeing.png"))

if min(mednormcoeffsigmas) <= 0.0001:
    print("####### WARNING : some normcoefferrs seem to be zero ! #############")
    print("Check/redo the normalization (with more stars ?), otherwise some of my error bars might be too small.")
    

# We rescale the sky level in the same way as for source fluxes :
medrelskylevels = np.asarray(medskylevels) * np.asarray(mednormcoeffs)

# The flags for nights (True if the night is OK) :
nightseeingbad = np.asarray(medseeings) < nightmaxseeing
print("Night seeing > %.2f : %i" % (nightmaxseeing, np.sum(nightseeingbad == False)))
nightellbad = np.asarray(medells) < nightmaxell
print("Night ell > %.2f : %i" % (nightmaxell, np.sum(nightellbad == False)))
nightskylevelbad = medrelskylevels < nightmaxrelskylevel
print("Night relskylevel > %.2f : %i" % (nightmaxrelskylevel, np.sum(nightskylevelbad == False)))
nightnormcoeffbad = np.asarray(mednormcoeffs) < nightmaxnormcoeff
print("Night normcoeff > %.2f : %i" % (nightmaxnormcoeff, np.sum(nightnormcoeffbad == False)))
nightnbimgbad = np.asarray(nbimgs) >= nightminnbimg
print("Night nbimg < %i : %i" % (nightminnbimg, np.sum(nightnbimgbad == False)))

flags = np.logical_and(np.logical_and(nightseeingbad, nightellbad), np.logical_and(nightskylevelbad, nightnormcoeffbad))
flags = np.logical_and(flags, nightnbimgbad)

print("%i nights are flagged as bad (i.e., they have flag = False)." % (np.sum(flags == False)))

# We prepare a structure for the rdb file. It is an ordered list of dicts, each dict has two keys : column name and the data.
exportcols = [
    {"name": "mhjd", "data": mhjds},
    {"name": "datetime", "data": meddates},
    {"name": "telescope", "data": telescopenames},
    {"name": "setname", "data": setnames},
    {"name": "nbimg", "data": nbimgs},
    {"name": "fwhm", "data": medseeings},
    {"name": "ellipticity", "data": medells},
    {"name": "airmass", "data": medairmasses},
    {"name": "relskylevel", "data": medrelskylevels},
    {"name": "normcoeff", "data": mednormcoeffs},
    {"name": "flag", "data": flags}
]

# Finally, calculating the median mags and errors for the sources :

"""
Summary of magerrs
------------------

All errors are computed for the *mean/median* of a night's measurements (i.e. "divided by sqrt(nbimgs)")

0 : theoretical shotnoise error only, (i.e. we assume there is no normalization error)

1 : combination of theoretical shotnoise and empirical normalization error. So this error is larger than error 0.
    (Malte : medians taken "where they should")
2 : like 1 (same ingredients), but the medians are taken before the normalisation
    (Malte : finds this strange)
3 : like 1 (same ingredients), but the medians are taken "later"
    (Malte : potentially less robust if many outliers).

4 : empirical error based on the MAD of the measurements within a night

5 : maximum of 1, 4

To add : the same but for single images of that night, i.e., without dividing by sqrt(nbimgs)
6 : theoretical shotnoise errror only
7 : shotnoise + renorm
8 : mad

"""

for i, sourcename in enumerate(sourcenames):

    fluxfieldname = f"out_{deconvname}_{sourcename}_flux"
    shotnoisefieldname = f"out_{deconvname}_{sourcename}_shotnoise"
    combierrorfieldname = f"out_{deconvname}_{sourcename}_combierr"

    # Getting the normalized median fluxes, and converting them to mags :
    normfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['median'])
    if not np.all(normfluxes > 0.0):
        raise RuntimeError("Negative Fluxes  !")
    mags = -2.5 * np.log10(normfluxes)

    ##### Errorbar 0 : shotnoise error of a typicial individual image in this night divided by the sqrt of the number of images within the night
    normshotnoises = np.fabs(np.array(groupfct.values(nights, shotnoisefieldname, normkey=normcoeffname)['median']))
    normshotnoises = normshotnoises / sqrtnbimgs
    magerrs0 = 2.5 * np.log10(1.0 + normshotnoises / normfluxes)

    ##### Errorbar 1 : shotnoise combined with renormalization error, also divided by sqrtnbimgs.
    # We have already calculated the relative coeff errors. Turning them into absolute ones and combining with shotnoise :
    normnormcoefferrs = normfluxes * medrelnormcoeffsigmas / sqrtnbimgs  # We divide by sqrt n (normshotnoises is already divided, see error 0 !)
    normcombierrors = np.sqrt(normnormcoefferrs ** 2 + normshotnoises ** 2)
    magerrs1 = 2.5 * np.log10(1.0 + normcombierrors / normfluxes)

    # assert np.all(magerrs1 > magerrs0)

    ##### Errorbar 2 : Also the median shotnoise combined with median renormalization error of a typical image in this night.
    # The difference is that here (and only for the calculation of the error bar),
    # the median of the fluxes is taken even before normalization (Why ?? Bad idea I think).
    # As always, the genreral formula for the combined error of flux*normcoeff = sqrt(normcoeff**2 * shotnoise**2 + flux**2 * normcoefferr**2).
    medfluxes = np.array(groupfct.values(nights, fluxfieldname, normkey=None)['median'])
    medshotnoises = np.fabs(np.array(groupfct.values(nights, shotnoisefieldname, normkey=None)['median']))
    medcombierrors = np.sqrt(
        (np.asarray(mednormcoeffs) ** 2 * medshotnoises ** 2) + (medfluxes ** 2 * mednormcoeffsigmas ** 2)) / sqrtnbimgs
    magerrs2 = 2.5 * np.log10(1.0 + medcombierrors / normfluxes)

    ##### Errorbar 3 : Median of combined error per image (of shotnoise and renormerr), divided by the number of images per night
    # The ingredients are the same as for errorbar 1, just the medians are taken "later".
    combinighterrors = np.fabs(np.array(groupfct.values(nights, combierrorfieldname, normkey=None)['median']))
    combinighterrors = combinighterrors / sqrtnbimgs
    magerrs3 = 2.5 * np.log10(1.0 + combinighterrors / normfluxes)

    ##### Errorbar 4 : MAD estimator of the spread of photometric measurements within this night,
    # scaled by a factor assuming a gaussian distribution, and divided by the sqrtnbimgs.
    # http://en.wikipedia.org/wiki/Median_absolute_deviation
    # Nights with less than 3 images get 3 times the median error.
    normmads = np.array(groupfct.values(nights, fluxfieldname, normkey=normcoeffname)['mad'])
    normmads = normmads / sqrtnbimgs
    normmads *= 1.4826
    magerrs4 = 2.5 * np.log10(1.0 + normmads / normfluxes)
    magerrs4[np.array(nbimgs) < 3] = 3.0 * np.median(magerrs4)

    ##### Errorbar 5 : maximum of theoretical and pragmatic errorbar
    magerrs5 = np.maximum(magerrs1, magerrs4)

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
    exportcols.append({"name": f"mag_{sourcename}", "data": mags})
    exportcols.append({"name": f"magerr_{sourcename}_0", "data": magerrs0})
    exportcols.append({"name": f"magerr_{sourcename}_1", "data": magerrs1})
    exportcols.append({"name": f"magerr_{sourcename}_2", "data": magerrs2})
    exportcols.append({"name": f"magerr_{sourcename}_3", "data": magerrs3})
    exportcols.append({"name": f"magerr_{sourcename}_4", "data": magerrs4})
    exportcols.append({"name": f"magerr_{sourcename}_5", "data": magerrs5})



# Done with all calculations, now we export this to an rdb file...
rdbexport.writerdb(exportcols, os.path.join(configdir, outputname + ".rdb"), writeheader=writeheader)


# And make a plot just for the fun of it.
fig2 = plt.figure(figsize=(20, 12))
fig2.subplots_adjust(left=0.06, right=0.98, bottom=0.1, top=0.95, wspace=0.1, hspace=0.1)

for i, sourcename in enumerate(sourcenames):
    mags = [col for col in exportcols if col["name"] == f"mag_{sourcename}"][0]["data"]
    magerrs = [col for col in exportcols if col["name"] == f"magerr_{sourcename}_5"][0]["data"]

    plt.errorbar(mhjds, mags, yerr=magerrs, linestyle="None", marker=".", label=sourcename)
    # Circles around flagged points :

    plt.plot(np.asarray(mhjds)[flags == False], np.asarray(mags)[flags == False], linestyle="None", marker="o",
             markersize=8., markeredgecolor="black", markerfacecolor="None", color="black")
    rms, mean_error = variousfct.measure_rms_scatter(mhjds, mags, magerrs, time_chunk=20)
    print (f"Image {sourcename} :  rms scatter {np.median(rms):2.4f} mag, mean photometric error : {np.median(mean_error):2.4f} mag")


# reverse y axis for magnitudes :
ax = plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds) - 100.0, np.max(mhjds) + 100.0)  # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

# plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [day]')
plt.ylabel('Magnitude (instrumental)')

plt.legend()
# leg = ax.legend(loc='upper right', fancybox=True)
# leg.get_frame().set_alpha(0.5)
leg = ax.legend(loc='lower right')
# leg.get_frame().set_alpha(0.5)

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
    fig2.savefig(os.path.join(configdir, outputname + "_plot.pdf"))
    print("Wrote plot.")
else:
    fig2.savefig(os.path.join(configdir, outputname + "_plot.pdf"))
    print("Wrote plot.")


plt.clf()

# Visualization of all those different error bars...

fig3 = plt.figure(figsize=(14, 2.0 * len(sourcenames)))
fig3.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.1, hspace=0.15)

for i, sourcename in enumerate(sourcenames):
    ax = plt.subplot(len(sourcenames), 1, i + 1)
    for errori in ["0", "1", "2", "3", "4", "5"]:
        magerrs = [col for col in exportcols if col["name"] == f"magerr_{sourcename}_{errori}"][0]["data"]
        ax.plot(np.array(mhjds) + 0.5 * int(errori), magerrs, marker=".", label=f"Error {errori}")

    ax.annotate(sourcename, xy=(0.03, 0.8), xycoords='axes fraction', color="black", fontsize=20)

ax.legend()

if showplots == True:
    plt.show()
else:
    fig3.savefig(os.path.join(configdir, outputname + "_plot_magerrs.pdf"))
    print("Wrote plot.")

print("Done.")
