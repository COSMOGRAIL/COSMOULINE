"""
We group the points per night.
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

print "You want to analyze the deconvolution %s" % deckey
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

images = db.select(imgdb, [deckeyfilenum,'gogogo'], ['\d\d*', True], returnType='dict', useRegExp=True, sortFields=['mjd'])
print "%i images" % len(images)

groupedimages = combibynight_fct.groupbynights(images)
print "%i nights" % len(groupedimages)

fieldnames = db.getFieldNames(imgdb)

plt.figure(figsize=(15, 15))

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

# deckeynormused = "medcoeff"
magtot = []
magerrtot = []
fluxvalstot =[]
fluxvalserrtot =[]

# colors = ["red", "blue", "purple", "green"]
for j, s in enumerate(ptsources):
    fluxfieldname = "out_%s_%s_flux" % (deckey, s.name)
    randomerrorfieldname = "out_%s_%s_shotnoise" % (deckey, s.name)

    mags = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused)['median']
    # errors = combibynight_fct.mags(groupedimages, fluxfieldname, normkey=deckeynormused)['median']


    absfluxerrors = np.array(
        combibynight_fct.values(groupedimages, randomerrorfieldname, normkey=deckeynormused)['median'])
    fluxvals = np.array(combibynight_fct.values(groupedimages, fluxfieldname, normkey=deckeynormused)['median'])

    # relfluxerrors = absfluxerrors / fluxvals
    # magerrorbars = -2.5*np.log10(relfluxerrors)

    # print magerrorbars

    upmags = -2.5 * np.log10(fluxvals + absfluxerrors)
    downmags = -2.5 * np.log10(fluxvals - absfluxerrors)
    magerrorbars = (downmags - upmags) / 2.0
    if lc_to_sum != None :
        if s.name != lc_to_sum[0] and s.name!=lc_to_sum[1] :
            plt.figure(1)
            plt.errorbar(mhjds, mags, yerr=[upmags - mags, mags - downmags], linestyle="None", marker=".", label=s.name)
    else :
        plt.errorbar(mhjds, mags, yerr=[upmags - mags, mags - downmags], linestyle="None", marker=".", label=s.name)
    # exportcols.extend([{"name":"mag_%s" % ptsrc.name, "data":mags}, {"name":"magerr_%s" % ptsrc.name, "data":2.0*magerrorbars}])
    magtot.append(mags)
    magerrtot.append(magerrorbars)
    fluxvalstot.append(fluxvals)
    fluxvalserrtot.append(absfluxerrors)



# for el in exportcols:
#	print len(el["data"])

# rdbexport.writerdb(exportcols, "out.rdb", True)

###########################################################
# Estimate the scatter index :


magerrtot = np.asarray(magerrtot)
magtot = np.asarray(magtot)
fluxvalstot = np.asarray(fluxvalstot)
fluxvalserrtot = np.asarray(fluxvalserrtot)
print np.shape(magtot)

if not lc_to_sum == None:
    if not len(lc_to_sum) == 2:
        print "I can sum only two light curves !"
        exit()
    magtot_sum = np.zeros((len(magtot[:, 0])-1,len(magtot[0,:])))
    magerrortot_sum = np.zeros((len(magtot[:, 0])-1,len(magtot[0,:])))
    ptsources_str = []

    i = [i for i,source in enumerate(ptsources) if source.name==lc_to_sum[0] or source.name==lc_to_sum[1]]
    fluxvalstot_sum = [fluxvalstot[i[0]]+fluxvalstot[i[1]]]
    ptsources_str = [ptsources[i[0]].name + "+"+ptsources[i[1]].name]
    magtot_sum[0,:] = -2.5*np.log10(fluxvalstot_sum)
    fluxerr_sum = [np.sqrt(fluxvalserrtot[i[0]]**2+fluxvalserrtot[i[1]]**2)]
    fluxerr_sum= np.asarray(fluxerr_sum)
    fluxvalstot_sum= np.asarray(fluxvalstot_sum)
    upmags = -2.5 * np.log10(fluxvalstot_sum + fluxerr_sum)
    downmags = -2.5 * np.log10(fluxvalstot_sum - fluxerr_sum)
    magerrortot_sum[0,:]= (downmags - upmags) / 2.0
    plt.errorbar(mhjds, magtot_sum[0,:], yerr=magerrortot_sum[0,:], linestyle="None", marker=".",label=ptsources_str[0])

    z =1
    for j in range(len(magtot)):
        if j != i[0] and j!=i[1]:
            magtot_sum[z,:] = magtot[j,:]
            magerrortot_sum[z,:] = magerrtot[j,:]
            ptsources_str.append(ptsources[j].name)
            z+=1

    magerrtot = magerrortot_sum
    magtot = magtot_sum

else :
    ptsources_str = [s.name for s in ptsources]

#make the plots :
plt.grid(True)
# reverse y axis for magnitudes :
ax = plt.gca()
ax.set_ylim(ax.get_ylim()[::-1])
ax.set_xlim(np.min(mhjds)-20, np.max(mhjds)+20)  # DO NOT REMOVE THIS !!!
# IT IS IMPORTANT TO GET THE DATES RIGHT

# plt.title(deckey, fontsize=20)
plt.xlabel('MHJD [days]')
plt.ylabel('Magnitude (instrumental)')

titletext1 = "%s (%i nights)" % (xephemlens.split(",")[0], len(groupedimages))
titletext2 = deckey

ax.text(0.02, 0.98, titletext1, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)
ax.text(0.02, 0.95, titletext2, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)

if plotnormfieldname:
    titletext3 = "Renormalized with %s" % (plotnormfieldname)
    ax.text(0.02, 0.92, titletext3, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)


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


#compute the dispersion estimator :
print ptsources_str
nsource = len(magtot[:, 0])
color = ['b', 'g' , 'r' , 'm', 'k', 'y']
n_source = len(ptsources_str)
chi_vec = np.zeros(n_source)
med_vec = np.zeros(n_source)
chitot = 0.0
counttot = 0.0
weitot = []

for k, s in enumerate(ptsources_str):
    mags = magtot[k, :]
    magerrorbars = magerrtot[k, :]
    plt.figure(2)
    plt.errorbar(mhjds, mags, yerr=magerrorbars, fmt='+', color=color[k])
    chi = 0.0
    count = 0.0
    countnan =0.0
    wei = []

    for i in range(len(mhjds) - 2):
        if (mhjds[i + 2] - mhjds[i]) > 20:
            continue
        a = (mags[i] - mags[i + 2]) / (mhjds[i] - mhjds[i + 2])
        b = mags[i] - a * mhjds[i]
        plt.plot([mhjds[i], mhjds[i + 2]], [mags[i], mags[i + 2]], 'r')
        w = np.abs(mags[i + 1] - (a * mhjds[i + 1] + b)) / magerrorbars[i + 1]

        if not np.isnan(w):
            wei.append(w)
            weitot.append(w)
            count += 1.0
            counttot += 1.0
            chi += w
            chitot += w
        else :
            countnan +=1.0

    wei = np.asarray(wei)
    chi_vec[k] = chi / count
    med_vec[k] = np.median(wei)
    print "#####################"
    print "SOURCE ", s
    print "number of points taken : ", len(wei)
    print "chi :", chi
    print "chi red (mean weight):", chi / count
    print "median weight :", np.median(wei)

print "#####################"
print "ALL LIGHTCURVES :"
print "number of points taken : ", len(weitot)
print "chi :", chitot
print "chi red (mean weight):", chitot / counttot
print "median weight :", np.median(weitot)
print "I wasn't able to compue the chi2 for %i datapoints (NaN)"%countnan

pos = 0.03
titletext4 = ""
for i,s in enumerate(ptsources_str):
    titletext4 += "$\chi^2_{" + s + "}$" + " = " + str(round(chi_vec[i]*1000)/1000.0) + " , $med_{" + s + "}$= " + str(round(med_vec[i]*1000)/1000.) + ", "

titletext4 += "all lightcurves : $\chi^2_{tot}$" + " = " + str(round((chitot/counttot)*1000)/1000.0) + " ,  $med_{tot}$= "  + str(round(np.median(weitot)*1000)/1000.0)

plt.figure(1)
ax.text(0.02, pos, titletext4, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)

if savefigs:
    if plotnormfieldname:
        if lc_to_sum == None:
            plotfilepath = os.path.join(plotdir, "%s_lc_%s_by_night.pdf" % (deckey, plotnormfieldname))
        else :
            plotfilepath = os.path.join(plotdir, "%s_lc_%s_by_night_sum.pdf" % (deckey, plotnormfieldname))
    else:
        if lc_to_sum == None:
            plotfilepath = os.path.join(plotdir, "%s_lc_by_night.pdf" % (deckey))
        else :
            plotfilepath = os.path.join(plotdir, "%s_lc_by_night_sum.pdf" % (deckey))
    plt.savefig(plotfilepath)
    print "Wrote %s" % (plotfilepath)
    plt.show()
else:
    plt.show()