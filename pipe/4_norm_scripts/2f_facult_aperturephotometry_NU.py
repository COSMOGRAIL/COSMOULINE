"""
New version of the aperture photometry ONLY
multiplot + information to help discarding some images.
"""
import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import configdir, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import readimagelist
from modules import star

sexphotomname = settings['sexphotomname']
workdir = settings['workdir']

import matplotlib.pyplot as plt

db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

# remove saturated
skipimages = [image[0] for image in
              readimagelist(os.path.join(configdir, 'saturatedlist.txt'))]  # image[1] would be the comment
# print "Something special here: I do not plot images that you put in saturatedlist.txt"
images = [image for image in images if not image['imgname'] in skipimages]

# images = [image for image in images if image["setname"] in ["3"]]
images = [image for image in images if image["seeing"] < 1.4]

nbrofimages = len(images)
print("I respect treatme, saturatedlist and other keywords defined in the script, and selected only %i images" % (
    nbrofimages))

# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

# Select only the desired stars and aperture
"""
starslist = ["a", "b", "d", "e", "f", "g", "h", "r", "w"]
starstoplot = ["a", "b", "d"]
normcoeffstarslist = [["a", "b", "d", "g"], ["a", "b", "d", "e", "f", "g", "h", "r", "w"], ["e", "f", "h", "r", "w"]]
#normcoeffstarslist = [["a"], ["b"], ["c"], ["d"], ["o"]]
"""

starslist = ["a", "b", "c", "d"]
starstoplot = ["a", "b", "c", "d"]
normcoeffstarslist = [["a", "b", "c", "d"]]
# normcoeffstarslist = [["a"], ["b"], ["c"], ["d"], ["o"]]

aperture = 'auto'  # for 30, put ap30

######## blah blah blah blah ########

photomstars = [s for s in photomstars if s.name in starslist]

print("These is the subset of photom stars I will treat here :")
print("Aperture is defined as: %s" % aperture)
print("\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars]))

colors = ['crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver',
          'yellow']

# get all obsnights
dates = sorted(list(set([image["date"] for image in images])))
roundmjds = sorted(list(set([round(image["mjd"]) for image in images])))

############################################################################################################
########
######## LIGHT CURVE PER EXPOSURE, NORMALISED BY A NORMCOEFF OF YOUR CHOICE
######## PART 1 - Per night
########
############################################################################################################

# Compute the mag and magerr, and normalise them with respect to a normalisation coefficient.
# Plot per exposure, for a given date.

filters = ["g", "r", "i", "z"]

if 0:

    for ind, mjd in enumerate(roundmjds):

        print("===== Night %i/%i =====" % (ind + 1, len(roundmjds)))

        plt.figure(figsize=(10 * len(normcoeffstarslist), 3 * len(starstoplot)))

        for indn, normcoeffstars in enumerate(normcoeffstarslist):
            nightimages = [image for image in images if round(image["mjd"]) == mjd]
            # nightimages = images
            # nightimages = [image for image in images if filter in image['imgname']]

            # assure that each star has a measured flux
            for ind, s in enumerate(photomstars):
                nightimages = [image for image in nightimages if
                               image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)] != None]

            # sort by date
            photomimages = list(sorted(nightimages, key=lambda image: image['mjd']))

            # get the fluxes, to compute the normcoeff
            normfluxes = []
            for ind, s in enumerate([s for s in photomstars if s.name in normcoeffstars]):
                normfluxes.append(
                    [float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for
                     image in photomimages])

            # compute the normcoeffs
            normcoeffs = []
            for ind in np.arange(len(normfluxes[0])):
                normcoeffs.append(np.mean([normflux[ind] for normflux in normfluxes]))

            # now loop on the stars to plot and divide by the norm coeff
            lcs = []

            for ind, s in enumerate([s for s in photomstars if s.name in starstoplot]):
                lc = {}
                lc["name"] = s.name

                # get the fluxes
                fluxes = [float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"])
                          for image in photomimages]
                fluxerrs = [
                    float(image["%s_%s_%s_flux_err" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for
                    image in photomimages]
                mjds = [float(image["mjd"]) for image in photomimages]

                # renormalise
                renormcoeffs = [float(coeff) / np.median(normcoeffs) for coeff in normcoeffs]
                renormfluxes = [float(flux) / renormcoeff for flux, renormcoeff in zip(fluxes, renormcoeffs)]
                renormfluxestop = [float(flux + fluxerr) / renormcoeff for flux, fluxerr, renormcoeff in
                                   zip(fluxes, fluxerrs, renormcoeffs)]
                renormfluxesbottom = [float(flux - fluxerr) / renormcoeff for flux, fluxerr, renormcoeff in
                                      zip(fluxes, fluxerrs, renormcoeffs)]

                mags = -2.5 * np.log10(renormfluxes)
                magstop = -2.5 * np.log10(renormfluxestop)
                magsbottom = -2.5 * np.log10(renormfluxesbottom)

                lc["mjds"] = mjds
                lc["flux"] = renormfluxes
                lc["fluxerr"] = fluxerrs
                lc["magnitude"] = mags
                lc["magerrtop"] = [magtop - mag for magtop, mag in zip(magstop, mags)]
                lc["magerrbottom"] = [mag - magbottom for magbottom, mag in zip(magsbottom, mags)]

                plt.subplot(len(starstoplot), len(normcoeffstarslist), ind * len(normcoeffstarslist) + (indn + 1))
                plt.errorbar(lc["mjds"], lc["magnitude"], yerr=[lc["magerrbottom"], lc["magerrtop"]], label=s.name,
                             color=colors[ind], linewidth=2)
                nightlen = float(len(lc["mjds"]))

                yerrmag = [[np.mean(lc["magerrbottom"]) / np.sqrt(nightlen)],
                           [np.mean(lc["magerrtop"]) / np.sqrt(nightlen)]]
                yerrstd = [[np.std(lc["magnitude"]) / np.sqrt(nightlen)], [np.std(lc["magnitude"]) / np.sqrt(nightlen)]]

                plt.errorbar(np.mean(lc["mjds"]), np.mean(lc["magnitude"]), yerr=yerrmag, color="grey", linewidth=4)
                plt.errorbar(np.mean(lc["mjds"]), np.mean(lc["magnitude"]), yerr=yerrstd, color="black", linewidth=1.5)
                plt.legend()

                if ind == 0:
                    plt.title('Renormalised by %s' % (''.join(normcoeffstars)))
                lcs.append(lc)
                plt.annotate("Error on the mean : +/- %.1f mmag\n Median absolute deviation : +/- %.1f mmag" % (
                float(yerrstd[0][0] * 1000),
                float(np.median(np.fabs(lc["magnitude"] - np.median(lc["magnitude"]))) * 1000)), xy=(0.2, 1.0),
                             xycoords='axes fraction',
                             xytext=(10, -10), textcoords='offset points', ha='center', va='top', fontsize=8)

            try:
                specialkw = nightimages[0]["date"]
            except:
                specialkw = 'wutwutwut'

            plt.suptitle("Aperture %s pixels  - %s" % (aperture, specialkw), fontsize=20)
            plt.xlabel("modified julian days", fontsize=15)
            plt.ylabel("magnitude (instrumental)", fontsize=15)

        plt.show()
        # sys.exit()
        # plt.savefig(os.path.join(workdir, "plots", "stars_aperture%s_%s.png" % (aperture, specialkw)))
        # writepickle(lcs, "results/lcs_renorm%s_%s.pkl" % (''.join(normcoeffstars), specialkw))
        # plt.show()
        # sys.exit()
        plt.close()

############################################################################################################
########
######## LIGHT CURVE PER EXPOSURE, NORMALISED BY A NORMCOEFF OF YOUR CHOICE
######## PART 2 - Median per night over all season
########
############################################################################################################

# Compute the mag and magerr, and normalise them with respect to a normalisation coefficient.
# Plot per exposure, for a given date.

if 1:

    plt.figure(figsize=(8 * len(normcoeffstarslist), 3 * len(starstoplot)))
    nightimages = images  # all the images !!

    for indn, normcoeffstars in enumerate(normcoeffstarslist):

        # assure that each star has a measured flux
        for ind, s in enumerate(photomstars):
            nightimages = [image for image in nightimages if
                           image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)] != None]

        # sort by date
        photomimages = list(sorted(nightimages, key=lambda image: image['mjd']))

        # get the fluxes, to compute the normcoeff
        normfluxes = []
        for ind, s in enumerate([s for s in photomstars if s.name in normcoeffstars]):
            normfluxes.append(
                [float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for image
                 in photomimages])

        # compute the normcoeffs
        normcoeffs = []
        for ind in np.arange(len(normfluxes[0])):
            normcoeffs.append(np.mean([normflux[ind] for normflux in normfluxes]))

        # now loop on the stars to plot and divide by the norm coeff

        for ind, s in enumerate([s for s in photomstars if s.name in starstoplot]):
            lc = {}
            lc["name"] = s.name

            # get the fluxes
            fluxes = [float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for
                      image in photomimages]
            fluxerrs = [float(image["%s_%s_%s_flux_err" % (sexphotomname, s.name, aperture)]) / float(image["exptime"])
                        for image in photomimages]
            mjds = [float(image["mjd"]) for image in photomimages]

            # renormalise
            renormcoeffs = [float(coeff) / np.median(normcoeffs) for coeff in normcoeffs]
            renormfluxes = [float(flux) / renormcoeff for flux, renormcoeff in zip(fluxes, renormcoeffs)]
            renormfluxestop = [float(flux + fluxerr) / renormcoeff for flux, fluxerr, renormcoeff in
                               zip(fluxes, fluxerrs, renormcoeffs)]
            renormfluxesbottom = [float(flux - fluxerr) / renormcoeff for flux, fluxerr, renormcoeff in
                                  zip(fluxes, fluxerrs, renormcoeffs)]

            mags = -2.5 * np.log10(renormfluxes)
            magstop = -2.5 * np.log10(renormfluxestop)
            magsbottom = -2.5 * np.log10(renormfluxesbottom)

            lc["mjds"] = mjds
            lc["flux"] = renormfluxes
            lc["fluxerr"] = fluxerrs
            lc["magnitude"] = mags
            lc["magerrtop"] = [magtop - mag for magtop, mag in zip(magstop, mags)]
            lc["magerrbottom"] = [mag - magbottom for magbottom, mag in zip(magsbottom, mags)]

            # compute the median per night
            medmjds = []
            medmags = []
            medmagerrtops = []
            medmagerrbottoms = []
            for rmjd in roundmjds:
                medmjds.append(np.median([mymjd for mymjd in lc["mjds"] if round(mymjd) == rmjd]))
                medmags.append(
                    np.median([mag for (mag, mymjd) in zip(lc["magnitude"], lc["mjds"]) if round(mymjd) == rmjd]))
                medmagerrtops.append(np.median(
                    [mag for (mag, mymjd) in zip(lc["magerrtop"], lc["mjds"]) if round(mymjd) == rmjd]) / np.sqrt(
                    len([mag for (mag, mymjd) in zip(lc["magerrtop"], lc["mjds"]) if round(mymjd) == rmjd])))
                medmagerrbottoms.append(np.median(
                    [mag for (mag, mymjd) in zip(lc["magerrbottom"], lc["mjds"]) if round(mymjd) == rmjd]) / np.sqrt(
                    len([mag for (mag, mymjd) in zip(lc["magerrtop"], lc["mjds"]) if round(mymjd) == rmjd])))

            plt.subplot(len(starstoplot), len(normcoeffstarslist), ind * len(normcoeffstarslist) + (indn + 1))
            plt.errorbar(medmjds, medmags, yerr=[medmagerrtops, medmagerrbottoms], label=s.name, color=colors[ind],
                         linewidth=2, fmt='o')

            plt.axis([np.nanmin(medmjds), np.nanmax(medmjds), np.nanmin(lc["magnitude"]) + 1.2 * np.nanmax(lc["magerrbottom"]),
                      np.nanmax(lc["magnitude"]) - 1.2 * np.nanmax(lc["magerrtop"])])

            plt.legend()
            if ind == 0:
                plt.title('renormalised by %s' % ''.join(normcoeffstars))

    plt.suptitle("Aperture %s pixels" % aperture, fontsize=20)
    plt.xlabel("modified julian days", fontsize=15)
    plt.ylabel("magnitude (instrumental)", fontsize=15)

    plt.show()
    sys.exit()
    plt.savefig("results/stars_aperture%s_all.png" % aperture)
    plt.close()
