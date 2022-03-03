"""
Play the flux in various aperture photometry from sextractor catalogue
per star
per image
per night
per peronni pizza


Index of different plots:

- light curve per exposure, normalised with a ref. star
- ratio of blue/red star versus airmass, hourangle, or other kw.
- Variations with chip position (need to run extrascript/compute_refpos_FORS2.py first)
- Plot aperture photometry radii
- Flux for various apertures


"""

import numpy as np
import datetime
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import alidir, configdir, imgdb, settings, plotdir
from modules.kirbybase import KirbyBase
from modules.variousfct import readimagelist, writepickle
from modules.headerstuff import juliandate
from modules import star, f2n

askquestions = settings['askquestions']
sexphotomname = settings['sexphotomname']
refimgname = settings['refimgname']
workdir = settings['workdir']
sexphotomfields = settings['sexphotomfields']
emptyregion = settings['emptyregion']
lensregion = settings['lensregion']

import matplotlib.pyplot as plt
db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo', 'treatme'], [True, True], returnType='dict')

# remove saturated
skipimages = [image[0] for image in readimagelist(os.path.join(configdir,'saturatedlist.txt'))] # image[1] would be the comment
#print "Something special here: I do not plot images that you put in saturatedlist.txt"
images = [image for image in images if not image['imgname'] in skipimages]

nbrofimages = len(images)
print("I respect treatme, saturatedlist and other keywords defined in the script, and selected only %i images" % (nbrofimages))


# Read the manual star catalog :
photomstarscatpath = os.path.join(configdir, "photomstars.cat")
photomstars = star.readmancat(photomstarscatpath)

# Select only the desired stars and aperture
#starslist = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "l", "m", "o", "q", "r", "s", "t", "v", "w"]
#starslist = ["a", "b", "c", "d", "g", "o", "q", "n", "s"]
starslist = ["f", "k", "l", "m", "n"]
starstoplot = ["f", "k", "l", "m", "n"]
#starstoplot = ["a"]
amstarslist = ["a", "b"]
photomstars = [s for s in photomstars if s.name in starslist]
normcoeffstars = ["f", "k", "l", "m", "n"]

xkeyword = 'mjds'  # default : mjds. Can also be moondists or hourangles

aperture = 'auto'  # for 30, put ap30
mydates = ["2016-10-01"]

specialkw = 'WFI'  # keyword for the first plot


######## blah blah blah blah ########

print("These is the subset of photom stars I will treat here :")
print("Aperture is defined as: %s" % aperture)
print("\n".join(["%s\t%.2f\t%.2f" % (s.name, s.x, s.y) for s in photomstars]))
#proquest(askquestions)

# transform mydates in mjds
mymjds = []
for date in mydates:
	mymjds.append(round(juliandate(datetime.datetime.strptime(str(date + "T23:59:59"), "%Y-%m-%dT%H:%M:%S")) - 2400000.5))

colors = ['crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow', 'crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow', 'crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow']

# get all obsnights
dates = sorted(list(set([image["date"] for image in images])))
mjds = sorted(list(set([round(image["mjd"]) for image in images])))

print(dates)
print(mjds)
print(mymjds)


############################################################################################################
########
######## LIGHT CURVE PER EXPOSURE, NORMALISED BY A REFERENCE STAR
########
############################################################################################################

# Compute the mag and magerr, and normalise them with respect to a reference star.
# Plot per exposure, for a given date.
if 0:

	nightimages = [image for image in images if round(image["mjd"]) in mymjds]

	for normalstar in photomstars:  # loop on reference stars

		lcs = []
		plt.figure()

		# add stars photometry (from sextractor)
		colind = 0
		for ind, s in enumerate(photomstars):

			# discard images without flux:
			photomimages = [image for image in nightimages if image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)] != None  and image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)] != None]

			# sort images by date
			photomimages = list(sorted(photomimages, key=lambda image: image['mjd']))

			# Normalisation coefficient
			normcoeffs = [float(image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)]) / float(image["exptime"]) for image in photomimages]


			lc = {}
			lc["name"] = s.name

			fluxes = [float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for image in photomimages]

			fluxerrs = [float(image["%s_%s_%s_flux_err" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for image in photomimages]

			mjds = [float(image["mjd"]) for image in photomimages]


			# renormalise
			renormcoeffs = [coeff / np.mean(normcoeffs) for coeff in normcoeffs]
			renormfluxes = [flux / renormcoeff for flux, renormcoeff in zip(fluxes, renormcoeffs)]
			renormfluxestop = [(flux+fluxerr)/ renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]
			renormfluxesbottom = [(flux-fluxerr)/ renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]

			mags = -2.5*np.log10(renormfluxes)
			magstop = -2.5*np.log10(renormfluxestop)
			magsbottom = -2.5*np.log10(renormfluxesbottom)

			lc["mjds"] = mjds
			lc["flux"] = renormfluxes
			lc["fluxerr"] = fluxerrs
			lc["magnitude"] = mags
			lc["magerrtop"] = [magtop-mag for magtop, mag in zip(magstop, mags)]
			lc["magerrbottom"] = [mag-magbottom for magbottom, mag in zip(magsbottom, mags)]

			lcs.append(lc)

			if s.name in starstoplot:
				#plt.figure()
				#plt.suptitle("Star %s - aperture %s pixels" %(s.name, aperture), fontsize=20)
				#plt.plot(lc["mjds"], lc["magnitude"], label=s.name, color=colors[ind], linewidth=2)
				plt.errorbar(lc["mjds"], lc["magnitude"], yerr=[lc["magerrbottom"],lc["magerrtop"]], label=s.name, color=colors[colind], linewidth=2)
				colind = colind +1
				nightlen = float(len(lc["mjds"]))


				#print np.mean(lc["mjds"])
				#print np.mean(lc["magnitude"])
				yerrmag = [[np.mean(lc["magerrbottom"]) / np.sqrt(nightlen)], [np.mean(lc["magerrtop"]) / np.sqrt(nightlen)]]
				yerrstd = [[np.std(lc["magnitude"]) / np.sqrt(nightlen)], [np.std(lc["magnitude"]) / np.sqrt(nightlen)]]


				plt.errorbar(np.mean(lc["mjds"]), np.mean(lc["magnitude"]), yerr=yerrmag, color="grey", linewidth = 4)
				plt.errorbar(np.mean(lc["mjds"]), np.mean(lc["magnitude"]), yerr=yerrstd, color="black", linewidth = 1.5)



		plt.suptitle("Aperture %s pixels - renormalised by %s" %(aperture, normalstar.name), fontsize=20)
		plt.xlabel("modified julian days", fontsize = 15)
		plt.ylabel("magnitude (instrumental)", fontsize = 15)
		plt.legend()
		plt.show()
		plt.savefig("results/plot_renorm%s_%s.png" % (normalstar.name, specialkw))

		writepickle(lcs, "results/lcs_renorm%s_%s.pkl" % (normalstar.name, specialkw))

	plt.show()
	sys.exit()

############################################################################################################
########
######## LIGHT CURVE PER EXPOSURE, NORMALISED BY A NORMCOEFF OF YOUR CHOICE
########
############################################################################################################

# Compute the mag and magerr, and normalise them with respect to a normalisation coefficient.
# Plot per exposure, for a given date.
if 0:

	for mjd in mjds:

		#nightimages = [image for image in images if round(image["mjd"]) in mymjds]
		nightimages = [image for image in images if round(image["mjd"]) == mjd]


		# assure that each star has a measured flux
		for ind, s in enumerate(photomstars):
			nightimages = [image for image in nightimages if image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)] != None]

		# sort by date
		photomimages = list(sorted(nightimages, key=lambda image: image['mjd']))

		# get the fluxes, to compute the normcoeff
		normfluxes = []
		for ind, s in enumerate(photomstars):
			if s.name in normcoeffstars:
				normfluxes.append([float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for image in photomimages])


		# compute the normcoeffs
		normcoeffs = []
		for ind in np.arange(len(normfluxes[0])):
			normcoeffs.append(np.mean([normflux[ind] for normflux in normfluxes]))

		# now loop on the stars to plot and divide by the norm coeff

		plt.figure()

		lcs= []
		for ind, s in enumerate(photomstars):
			lc = {}
			lc["name"] = s.name

			# get the fluxes
			fluxes = [float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for image in photomimages]
			fluxerrs = [float(image["%s_%s_%s_flux_err" % (sexphotomname, s.name, aperture)]) / float(image["exptime"]) for image in photomimages]
			mjds = [float(image["mjd"]) for image in photomimages]


			# renormalise
			renormcoeffs = [float(coeff) / np.median(normcoeffs) for coeff in normcoeffs]
			renormfluxes = [float(flux) / renormcoeff for flux, renormcoeff in zip(fluxes, renormcoeffs)]
			renormfluxestop = [float(flux + fluxerr) / renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]
			renormfluxesbottom = [float(flux - fluxerr) / renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]

			mags = -2.5 * np.log10(renormfluxes)
			magstop = -2.5 * np.log10(renormfluxestop)
			magsbottom = -2.5 * np.log10(renormfluxesbottom)

			lc["mjds"] = mjds
			lc["flux"] = renormfluxes
			lc["fluxerr"] = fluxerrs
			lc["magnitude"] = mags
			lc["magerrtop"] = [magtop - mag for magtop, mag in zip(magstop, mags)]
			lc["magerrbottom"] = [mag - magbottom for magbottom, mag in zip(magsbottom, mags)]


			if s.name in starstoplot:

				plt.errorbar(lc["mjds"], lc["magnitude"], yerr=[lc["magerrbottom"],lc["magerrtop"]], label=s.name, color=colors[ind], linewidth=2)
				nightlen = float(len(lc["mjds"]))

				yerrmag = [[np.mean(lc["magerrbottom"]) / np.sqrt(nightlen)], [np.mean(lc["magerrtop"]) / np.sqrt(nightlen)]]
				yerrstd = [[np.std(lc["magnitude"]) / np.sqrt(nightlen)], [np.std(lc["magnitude"]) / np.sqrt(nightlen)]]

				print(yerrstd)

				plt.errorbar(np.mean(lc["mjds"]), np.mean(lc["magnitude"]), yerr=yerrmag, color="grey", linewidth=4)
				plt.errorbar(np.mean(lc["mjds"]), np.mean(lc["magnitude"]), yerr=yerrstd, color="black", linewidth=1.5)

			lcs.append(lc)
		try:
			specialkw = nightimages[0]["date"]
		except:
			specialkw = 'wutwutwut'
		plt.suptitle("Aperture %s pixels - renormalized by %s - %s" % (aperture, ''.join(normcoeffstars), specialkw), fontsize=20)
		plt.xlabel("modified julian days", fontsize=15)
		plt.ylabel("magnitude (instrumental)", fontsize=15)
		plt.legend()
		plt.savefig("results/plot_renorm%s_%s.png" % (''.join(normcoeffstars), specialkw))
		#writepickle(lcs, "results/lcs_renorm%s_%s.pkl" % (''.join(normcoeffstars), specialkw))
		plt.show()
	sys.exit()

############################################################################################################
########
######## RATIO OF BLUE / RED STARS VERSUS AIRMASS, HOURANGLE, ETC... ADJUST KEYWORD IN THE SCRIPT
########
############################################################################################################

# Compute the mag and magerr, and normalise them with respect to a reference star.
# Plot the ratio of two stars versus the airmass
if 0:

		bluestarslist = ["a", "b", "c", "d"]
		redstarslist = ["h", "i", "w"]  # h, i, w

		amstarslists = []

		for bluestar in bluestarslist:
			for redstar in redstarslist:
				amstarslists.append([bluestar, redstar])

		for amstarslist in amstarslists:

			if amstarslist[0] == amstarslist[1]:
				pass
			else:

				lcs = []
				plt.figure()
				amstars = [s for s in photomstars if s.name in amstarslist]

				assert(len(amstarslist) == 2)

				# discard images without flux:
				photomimages = [image for image in images if image["%s_%s_%s_flux" % (sexphotomname, amstars[0].name, aperture)] != None and image["%s_%s_%s_flux" % (sexphotomname, amstars[1].name, aperture)] != None]

				# discard saturated images:
				saturatedlist = [line.split('\n')[0] for line in open(os.path.join(configdir, 'saturatedlist.txt')).readlines()]
				photomimages = [image for image in photomimages if image["imgname"] not in saturatedlist]


				# We divide the first star by the second star
				relfluxes = [float(image["%s_%s_%s_flux" % (sexphotomname, amstars[0].name, aperture)]) / float(image["%s_%s_%s_flux" % (sexphotomname, amstars[1].name, aperture)]) for image in photomimages]

				# airmass

				kw = 'hourangle'  # can be 'airmass' or 'moondist' or whatever else... adjust the bin values !!

				airmasses = [float(image[kw]) for image in photomimages]

				# Let's bin these in intervals of 0.1 airmass
				binstep =  2  #0.05
				minam = -15  # 1.0
				maxam = 15 #2.0
				bins = []
				mybinval = minam
				bininc = 0
				while mybinval < maxam:
					bins.append([minam + bininc, minam + bininc + binstep])
					bininc += binstep
					mybinval += binstep

				binnedam = []
				binnedratio = []
				binnederr = []
				for bin in bins:
					binnedam.append(np.median([float(image[kw]) for image in photomimages if image[kw] > bin[0] and image[kw] < bin[1]]))

					ratios = [float(image["%s_%s_%s_flux" % (sexphotomname, amstars[0].name, aperture)]) / float(image["%s_%s_%s_flux" % (sexphotomname, amstars[1].name, aperture)]) for image in photomimages if image[kw] > bin[0] and image[kw] < bin[1]]
					binnedratio.append(np.median(ratios))
					binnederr.append(np.std(ratios) / np.sqrt(len(ratios)))


				# and plot !
				plt.suptitle("Aperture %s pixels - %s / %s " %(aperture, amstars[0].name, amstars[1].name), fontsize=20)
				if kw == 'airmass':
					plt.subplot(2,1,1)
				plt.scatter(airmasses, relfluxes, s=10, alpha=0.5, label="obs")
				plt.errorbar(binnedam, binnedratio, yerr=binnederr, color="crimson", linewidth=3, label="median")
				#plt.xlabel("Airmass", fontsize = 15)
				plt.ylabel("Flux ratio", fontsize = 15)
				plt.legend()

				if kw == 'airmass':
					plt.subplot(2,1,2)
					plt.scatter(airmasses, relfluxes, s=10, alpha=0.5)
					plt.errorbar(binnedam, binnedratio, yerr=binnederr, color="crimson", linewidth=3)
					plt.xlabel("Airmass", fontsize = 15)
					plt.ylabel("Flux ratio", fontsize = 15)
					plt.axis([1, 1.7, np.median(binnedratio)-1.5*np.std(binnedratio), np.mean(binnedratio)+1*np.std(binnedratio)])


				#plt.savefig(os.path.join(plotdir, "Airmass_vs_fluxratio_%s_over_%s" %(amstars[0].name, amstars[1].name)))
		print("Plots saved :")
		print(os.path.join(plotdir, "Airmass_vs_fluxratio_*"))
		plt.show()
		sys.exit()

# Compute the mag and magerr per obsnight, and normalise them with respect to a reference star
if 0:

	for normalstar in photomstars:  # loop on reference stars

		lcs = []
		plt.figure()

		# add lens photometry (manual, from 0_getlensflux)
		lens = {}
		lens["name"] = "lens"
		normcoeffs = []
		lensfluxes = []
		lensmeanmjds = []
		lensmeanmoondists = []
		lensmeanhourangles = []

		# discard images without flux:
		photomimages = [image for image in images if image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)] != None]

		# discard saturated images:
		saturatedlist = [line.split('\n')[0] for line in open(os.path.join(configdir, 'saturatedlist.txt')).readlines()]

		photomimages = [image for image in photomimages if image["imgname"] not in saturatedlist]

		for date in dates:  #group by night

			if len([float(image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)]) for image in photomimages if image["date"] == date]) > 0:

				normcoeffs.append((sum([float(image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date])))

				lensfluxes.append(sum([float(image["manualflux_lens"]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date]))


				lensmeanmjds.append(np.mean([float(image["mjd"]) for image in photomimages if image["date"] == date]))
				lensmeanmoondists.append(np.mean([float(image["moondist"]) for image in photomimages if image["date"] == date]))
				#lensmeanhourangles.append(np.mean([float(image["hourangle"]) for image in photomimages if image["date"] == date]))

		lens["mjds"] = lensmeanmjds
		lens["moondists"] = lensmeanmoondists
		#lens["hourangles"] = lensmeanhourangles


		# renormalise
		renormcoeffs = [coeff / np.mean(normcoeffs) for coeff in normcoeffs]
		renormlensfluxes = [flux / renormcoeff for flux, renormcoeff in zip(lensfluxes, renormcoeffs)]
		lens["flux"] = renormlensfluxes
		lens["magnitude"] = -2.5*np.log10(renormlensfluxes)
		lcs.append(lens)
		linestyle = '--'
		plt.plot(lens['%s' % xkeyword], lens["magnitude"], label="lens", color="black", linewidth=2.5, linestyle=linestyle)
		#plt.scatter(lens["mjds"], lens["magnitude"], label="lens", color="black")


		# add stars photometry (from sextractor)
		for ind, s in enumerate(photomstars):
			# discard images without flux:
			photomimages = [image for image in images if image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)] != None  and image["%s_%s_ap30_flux" % (sexphotomname, normalstar.name)] != None]


			lc = {}
			lc["name"] = s.name
			fluxes = []
			fluxerrs = []
			meanmjds = []
			normcoeffs = []
			meanmoondists = []
			meanhourangles = []


			if 1:
				for date in dates:  #group by night

					if len([float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) for image in photomimages if image["date"] == date]) > 0 and \
					len([float(image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)]) for image in photomimages if image["date"] == date]) > 0:


						normcoeffs.append((sum([float(image["%s_%s_%s_flux" % (sexphotomname, normalstar.name, aperture)]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date])))

						fluxes.append(sum([float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date]))

						fluxerrs.append(sum([float(image["%s_%s_%s_flux_err" % (sexphotomname, s.name, aperture)]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date]))

						# WRONG ! Sum counts, not fluxes !!
						#fluxerrs.append(sum([float(image["%s_%s_ap%serr_flux" % (sexphotomname, s.name, aperture)])/float(image["exptime"]) for image in photomimages if image["date"] == date]) ) # / np.sqrt(len([image for image in photomimages if image["date"] == date])))

						meanmjds.append(np.mean([float(image["mjd"]) for image in photomimages if image["date"] == date]))
						meanmoondists.append(np.mean([float(image["moondist"]) for image in photomimages if image["date"] == date]))
						#meanhourangles.append(np.mean([float(image["hourangle"]) for image in photomimages if image["date"] == date]))

				# renormalise
				renormcoeffs = [coeff / np.mean(normcoeffs) for coeff in normcoeffs]
				renormfluxes = [flux / renormcoeff for flux, renormcoeff in zip(fluxes, renormcoeffs)]
				renormfluxestop = [(flux+fluxerr)/ renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]
				renormfluxesbottom = [(flux-fluxerr)/ renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]

				mags = -2.5*np.log10(renormfluxes)
				magstop = -2.5*np.log10(renormfluxestop)
				magsbottom = -2.5*np.log10(renormfluxesbottom)

				lc["mjds"] = meanmjds
				lc["moondists"] = meanmoondists
				#lc["hourangles"] = meanhourangles
				lc["flux"] = renormfluxes
				lc["fluxerr"] = fluxerrs
				lc["magnitude"] = mags
				lc["magerrtop"] = [magtop-mag for magtop, mag in zip(magstop, mags)]
				lc["magerrbottom"] = [mag-magbottom for magbottom, mag in zip(magsbottom, mags)]

				lcs.append(lc)

				#plt.figure()
				#plt.suptitle("Star %s - aperture %s pixels" %(s.name, aperture), fontsize=20)
				#plt.plot(lc["mjds"], lc["magnitude"], label=s.name, color=colors[ind], linewidth=2)

				fmt = '--o' if xkeyword == 'mjds' else 'o'
				plt.errorbar(lc['%s' % xkeyword], lc["magnitude"], yerr=[lc["magerrbottom"],lc["magerrtop"]], label=s.name, color=colors[ind], linewidth=2, fmt=fmt)



		plt.suptitle("Aperture %s pixels - renormalised by %s" % (aperture, normalstar.name), fontsize=20)
		xlabel = 'modified julian days' if xkeyword == 'mjds' else xkeyword
		plt.xlabel(xlabel, fontsize=15)
		plt.ylabel("magnitude (instrumental)", fontsize=15)
		plt.legend()
	plt.show()
	sys.exit()

# Let's do it again with a "per night" renormalisation (some kind of medcoeff, but per night)
# First, we stack all the images per night, then get the flux, then use it to compute a medcoeff
if 1:
	renormcoefftype = 'medcoeff'
	### get nightmedcoeffs:

	nightinfos = []
	for date in dates:  #group by night

		nightinfo = {}
		nightinfo["date"] = date

		for star_ in photomstars: # loop on stars
			photomimages = [image for image in images if image["%s_%s_%s_flux" % (sexphotomname, star_.name, aperture)] != None and image["date"] == date]	 # get the images with flux
			#starfluxpernight = 0 # if no flux available during the given night
			try:
				starfluxpernight = (sum([float(image["%s_%s_%s_flux" % (sexphotomname, star_.name, aperture)]) for image in photomimages]) / sum([float(image["exptime"]) for image in photomimages])) # this is the flux per night
			except ZeroDivisionError:
				starfluxpernight = 0.

			nightinfo["%s" %star_.name] = (star_.name, starfluxpernight)

		nightinfos.append(nightinfo)

	# reference night is the first one
		nightinfos[0]["medcoeff"] = 1.0
		nightinfos[0]["meancoeff"] = 1.0

	refnight = nightinfos[0]
	# compute the medcoeff of the other nights
	for nightinfo in nightinfos[1:]:
		#print "==== ",nightinfo["date"]," ===="
		fluxratios = []
		for star_ in photomstars:
			#print nightinfo[star.name], refnight[star.name], nightinfo[star.name][1] / refnight[star.name][1]
			try:
				fluxratios.append(nightinfo[star_.name][1] / refnight[star_.name][1])
			except ZeroDivisionError:
				print("No flux for star %s at night %s." %(star_.name, nightinfo["date"]))
			except:
				print("Error with star %s" % star_.name)
				sys.exit()
		#print "nightmeancoeff : ", np.mean(fluxratios)
		#print "nightmedcoeff : ", np.median(fluxratios)
		nightinfo["medcoeff"] = np.median(fluxratios)
		nightinfo["meancoeff"] = np.mean(fluxratios)

	# Now, nightinfo contains for each night the medcoeff and meancoeff. Let's use this to renormalise the flux from the lens and the individual stars before plotting their lightcurves.


	lcs = []
	plt.figure()

	# add lens photometry (manual, from 0_getlensflux)
	"""
	lens = {}
	lens["name"] = "lens"
	normcoeffs = []
	lensfluxes = []
	lensmeanmjds = []
	lensmeanmoondists = []
	lensmeanhourangles = []

	# discard images without flux:
	photomimages = [image for image in images if image["manualflux_lens"] != None]

	for date in dates:  #group by night

		if len([image for image in photomimages if image["date"] == date]) > 0:
			normcoeffs.append([nightinfo[renormcoefftype] for nightinfo in nightinfos if nightinfo["date"] == date][0])  # stupid, but it works
			lensfluxes.append(sum([float(image["manualflux_lens"]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date]))

			lensmeanmjds.append(np.mean([float(image["mjd"]) for image in photomimages if image["date"] == date]))
			lensmeanmoondists.append(np.mean([float(image["moondist"]) for image in photomimages if image["date"] == date]))
			lensmeanhourangles.append(np.mean([float(image["hourangle"]) for image in photomimages if image["date"] == date]))

	lens["mjds"] = lensmeanmjds


	# renormalise
	renormcoeffs = [coeff / np.mean(normcoeffs) for coeff in normcoeffs]
	renormlensfluxes = [flux / renormcoeff for flux, renormcoeff in zip(lensfluxes, renormcoeffs)]
	lens["flux"] = renormlensfluxes
	lens["magnitude"] = -2.5*np.log10(renormlensfluxes)



	lcs.append(lens)
	plt.plot(lens["mjds"], lens["magnitude"], label="lens", color="black", linewidth=2.5, linestyle='--')
	#plt.scatter(lens["mjds"], lens["magnitude"], label="lens", color="black")
	"""

	# add stars photometry (from sextractor)
	for ind, s in enumerate(photomstars):
		# discard images without flux:
		photomimages = [image for image in images if image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)] != None]


		lc = {}
		lc["name"] = s.name
		fluxes = []
		fluxerrs = []
		meanmjds = []
		normcoeffs = []
		#try:
		for date in dates:  #group by night

			if len([float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) for image in photomimages if image["date"] == date]) > 0:


				normcoeffs.append([nightinfo[renormcoefftype] for nightinfo in nightinfos if nightinfo["date"] == date][0])

				fluxes.append(sum([float(image["%s_%s_%s_flux" % (sexphotomname, s.name, aperture)]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date]))


				try:
					fluxerrs.append(sum([float(image["%s_%s_%serr_flux" % (sexphotomname, s.name, aperture)]) for image in photomimages if image["date"] == date]) / sum([float(image["exptime"]) for image in photomimages if image["date"] == date]))
				except:
					fluxerrs.append(0.)

				meanmjds.append(np.mean([float(image["mjd"]) for image in photomimages if image["date"] == date]))


		# renormalise
		renormcoeffs = [coeff / np.mean(normcoeffs) for coeff in normcoeffs]
		renormfluxes = [flux / renormcoeff for flux, renormcoeff in zip(fluxes, renormcoeffs)]
		renormfluxestop = [(flux+fluxerr)/ renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]
		renormfluxesbottom = [(flux-fluxerr)/ renormcoeff for flux, fluxerr, renormcoeff in zip(fluxes, fluxerrs, renormcoeffs)]

		mags = -2.5*np.log10(renormfluxes)
		magstop = -2.5*np.log10(renormfluxestop)
		magsbottom = -2.5*np.log10(renormfluxesbottom)

		lc["mjds"] = meanmjds
		lc["flux"] = renormfluxes
		lc["fluxerr"] = fluxerrs
		lc["magnitude"] = mags
		lc["magerrtop"] = [magtop-mag for magtop, mag in zip(magstop, mags)]
		lc["magerrbottom"] = [mag-magbottom for magbottom, mag in zip(magsbottom, mags)]

		lcs.append(lc)

		#plt.figure()
		#plt.suptitle("Star %s - aperture %s pixels" %(s.name, aperture), fontsize=20)
		#plt.plot(lc["mjds"], lc["magnitude"], label=s.name, color=colors[ind], linewidth=2)
		plt.errorbar(lc["mjds"], lc["magnitude"], yerr=[lc["magerrbottom"],lc["magerrtop"]], label=s.name, color=colors[ind], linewidth=2)


		#except:
			#print "Something wrong with star %s" %s.name
			#sys.exit()


	plt.suptitle("Aperture %s pixels - renormalised by %s" %(aperture, "medcoeff"), fontsize=20)
	plt.xlabel("modified julian days", fontsize = 15)
	plt.ylabel("magnitude (instrumental)", fontsize = 15)
	plt.legend()

	plt.show()
	sys.exit()

############################################################################################################
########
######## EXAMINE CHIP POSITION
########
############################################################################################################

if 0:
	"""
	I have 17 possible positions
	I have a subset of Ns starstoplot
	For each night, I have at least 17 exposure.

	I build a big list of dicts <3.
	The primary level is the chip position : 17 entries
		For each position, I have Ns stars
			For each star, I have Nimg values
	"""

	nonabs = False

	poses = []  # list of dict

	# get all possible positions on the chip
	refposlist = sorted(list(set([image["refpos"] for image in images])))

	# initialise the dicts
	for refpos in refposlist:
		mydict = {"pos": refpos}
		for star_ in starstoplot:
			mydict["star_%s" % str(star_)] = []

		poses.append(mydict)

	# fill the dicts, night by night, star by star
	for date in dates:
		subimgs = [image for image in images if image["date"] == date]

		for star_ in starstoplot:

			# discard images without flux
			photomimages = [image for image in subimgs if image["%s_%s_%s_flux" % (sexphotomname, star_, aperture)] != None]
			# do not compute if less than 5 images (to avoid biasing the scatter)
			if len(photomimages) > 5:
				median = np.median([float(image["%s_%s_%s_flux" % (sexphotomname, star_, aperture)]) / float(image["exptime"]) for image in photomimages])
				std = np.std([float(image["%s_%s_%s_flux" % (sexphotomname, star_, aperture)]) / float(image["exptime"]) for image in photomimages])

				for image in photomimages:
					flux = float(image["%s_%s_%s_flux" % (sexphotomname, star_, aperture)]) / float(image["exptime"])
					if nonabs:
						scatter = (flux - median) / std
					else:
						scatter = np.abs(flux - median) / std
					pos = image["refpos"]
					for d in poses:
						if d["pos"] == pos:
							d["star_%s" % str(star_)].append(scatter)


	# and plot
	colors = ['crimson', 'chartreuse', 'purple', 'cyan', 'gold', 'black', 'blue', 'magenta', 'brown', 'green', 'silver', 'yellow', 'red', 'white', 'skyblue', 'violet']


	for star_ in starstoplot:
		medscat = []
		stdscat = []
		occs = []
		plt.figure(figsize=(10, 8.3))
		for ind, d in enumerate(poses[1:]):
			#plt.hist(d["star_%s" %star], 50)
			medscat.append(np.median(d["star_%s" %star_]))
			stdscat.append(np.std(d["star_%s" %star_]))
			occs.append(len(d["star_%s" %star_]))

			plt.scatter(np.median(d["star_%s" %star_]), np.std(d["star_%s" %star_]), s=len(d["star_%s" %star_]), c=colors[ind], label=str(ind + 1) + ' | x%i' % len(d["star_%s" % star_]))

		#plt.scatter(ra, decs[ind], s=occs[ind]*3, c=colors[ind], marker='o', label=str(ind+1)+' | x%s' % occs[ind])
		leg = plt.legend(scatterpoints=1)
		leg.get_frame().set_alpha(1.0)
		plt.suptitle('Star %s - aperture %s' % (star_, aperture), fontsize=25)
		if nonabs:
			plt.xlabel(r'median$(\frac{flux-median(nightflux)}{std(nightflux)})$', fontsize=20)
			plt.ylabel(r'std$(\frac{flux-median(nightflux)}{std(nightflux)})$', fontsize=20)
			xmin, xmax, ymin, ymax = -0.6, 1.0, 0.77, 1.13  # for non abs
		else:
			plt.xlabel(r'median$(\frac{|flux-median(nightflux)|}{std(nightflux)})$', fontsize=20)
			plt.ylabel(r'std$(\frac{|flux-median(nightflux)|}{std(nightflux)})$', fontsize=20)
			xmin, xmax, ymin, ymax = 0.4, 1.0, 0.5, 0.77  # for abs

		if min(medscat) < xmin or max(medscat) > xmax or min(stdscat) < ymin or max(stdscat) > ymax:
			print("points are out of plot axis !")
			print("for star %s" % star_)
			#sys.exit()

		plt.axis([xmin, xmax, ymin, ymax])
	#plt.show()


	# Now, redo it without distinction between the stars.

	def conc(list):
		all = []
		for elt in list:
			for e in elt:
				all.append(e)
		return all

	plt.figure(figsize=(10, 8.3))
	for ind, d in enumerate(poses[1:]):
		medscat = []
		stdscat = []
		occs = []
		for star_ in starstoplot:
			medscat.append(d["star_%s" % star_])
			stdscat.append(d["star_%s" % star_])
			occs.append(len(d["star_%s" % star_]))

		plt.scatter(np.median(conc(medscat)), np.std(conc(stdscat)), s=sum(occs), c=colors[ind], label=str(ind + 1) + ' | x%i' % sum(occs))

	leg = plt.legend(scatterpoints=1)
	leg.get_frame().set_alpha(1.0)
	plt.suptitle('All stars - aperture %s' % aperture, fontsize=25)
	if nonabs:
		plt.xlabel(r'median$(\frac{flux-median(nightflux)}{std(nightflux)})$', fontsize=20)
		plt.ylabel(r'std$(\frac{flux-median(nightflux)}{std(nightflux)})$', fontsize=20)
		xmin, xmax, ymin, ymax = -0.6, 1.0, 0.77, 1.13  # for non abs
	else:
		plt.xlabel(r'median$(\frac{|flux-median(nightflux)|}{std(nightflux)})$', fontsize=20)
		plt.ylabel(r'std$(\frac{|flux-median(nightflux)|}{std(nightflux)})$', fontsize=20)
		xmin, xmax, ymin, ymax = 0.4, 1.0, 0.5, 0.77  # for abs
	plt.axis([xmin, xmax, ymin, ymax])
	plt.show()

	sys.exit()

############################################################################################################
########
######## DRAWING APERTURES
########
############################################################################################################


# draw apertures around the photomstars. You can tune the size of the apertures in the script below.
# keep in mind that you give me the radius of apertures to draw. But you gave sextractor the diameter.
if 0:
	"""
	Let's draw apertures of 20, 30, 40, 50 and 60 pixels around the photomstars
	"""
	# We convert the star objects into dictionnaries, to plot them using f2n.py
	# (f2n.py does not use these "star" objects...)

	refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
	refimage = refimage[0]

	refmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in photomstars]

	reffitsfile = os.path.join(alidir, refimage['imgname'] + "_skysub.fits")

	f2nimg = f2n.fromfits(reffitsfile)
	f2nimg.setzscale(z1=0, z2=1000)
	#f2nimg.rebin(2)
	f2nimg.makepilimage(scale = "log", negative = False)


	#f2nimg.drawstarlist(refautostarsasdicts, r = 30, colour = (150, 150, 150))
	#f2nimg.drawstarlist(refmanstarsasdicts, r = 25, colour = (0, 0, 255))
	f2nimg.drawstarlist(refmanstarsasdicts, r = 10, colour = (255, 0, 0))
	#f2nimg.drawstarlist(refmanstarsasdicts, r = 15, colour = (255, 0, 0))
	f2nimg.drawstarlist(refmanstarsasdicts, r = 20, colour = (255, 0, 0))
	#f2nimg.drawstarlist(refmanstarsasdicts, r = 25, colour = (255, 0, 0))
	#f2nimg.drawstarlist(refmanstarsasdicts, r = 30, colour = (255, 0, 0))


	f2nimg.writeinfo(["","Identified alignment stars with corrected sextractor coordinates : %i" % len( refmanstarsasdicts)], colour = (255, 0, 0))

	# We draw the rectangles around qso and empty region :

	lims = [list(map(int,x.split(':'))) for x in lensregion[1:-1].split(',')]
	f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Lens")

	lims = [list(map(int,x.split(':'))) for x in emptyregion[1:-1].split(',')]
	f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], colour=(0,255,0), label = "Empty")


	f2nimg.writetitle("Ref : " + refimage['imgname'])

	pngpath = os.path.join(workdir, "apertures_on_photomstars.png")
	f2nimg.tonet(pngpath)

	print("I have written a map into")
	print(pngpath)
	sys.exit()

############################################################################################################
########
######## FLUX VERSUS APERTURE
########
############################################################################################################

# For each star on each image, plot the flux versus the aperture for each entry I found in the database.
if 0:
	for i, image in enumerate(images[500:550]):

		if i < 1:
			print(" -" * 20)
			print(i+1, "/", nbrofimages, ":", image['imgname'])

			for s in photomstars:
					print("Star %s" %s.name)
					dbfields = [{"name":"%s_%s_%s" % (sexphotomname, s.name, f["dbname"]), "type":f["type"]} for f in sexphotomfields]
					apertures = []
					fluxerrs = []
					fluxes = []

					try:
						for field in dbfields:
							if 'auto' not in field["name"] and 'err' not in field["name"]:
								print(field["name"], image[field["name"]])
								fluxes.append(float(image[field["name"]]))
								apertures.append(int(field["name"].split('_')[2].split('ap')[1]))
							if 'auto' not in field["name"] and 'err' in field["name"]:
								print(field["name"], image[field["name"]])
								fluxerrs.append(float(image[field["name"]]))
							if 'auto' in field["name"] and 'err' not in field["name"]:
								print(field["name"], image[field["name"]])
								flux_auto = float(image[field["name"]])
							if 'auto' in field["name"] and 'err' in field["name"]:
								print(field["name"], image[field["name"]])
								flux_auto_err = float(image[field["name"]])

						plt.figure()
						#plt.plot(apertures, fluxes,'or-')
						plt.errorbar(apertures, fluxes, xerr=0, yerr=fluxerrs)
						plt.axhline(flux_auto)
						plt.suptitle('Star %s' % s.name)

					except:
						print("No fluxes for star %s on image %s" %(s.name, image["imgname"]))
			plt.show()
			continue
	sys.exit()
