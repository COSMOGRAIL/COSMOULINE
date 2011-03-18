#---------------------------------------------------------------------------


# The "working" dir where all the pipeline products will be *written*
# ("big-old-never-backuped-disk")
workdir = "/your/absolute/path/to/cosmouline_work/J1001"


#------------------------ SWITCHES -----------------------------------------


# A switch to tell if these testlist-flags should be used.
# If these flags are set, the scripts will run only on your subset of images.
thisisatest = False

# A switch to use soft links instead of true file copies whenever possible (you might not want this for some reasons)
uselinks = True

# A switch to make all scripts skip any questions
askquestions = True

# A switch to display image by image plots that are normally not needed. For debugging etc.
# If True, the database will not be updated !
# You should typically use this in connection with thisisatest = True ...
checkplots = False
	# This is used by : 1_character_scripts/4_skystats.py, 3b_measureseeing.py

# A switch to save figures that would otherwise be shown.
# Good to keep this on True if you work over a slow connection. Saved into plotdir.
savefigs = True

# A switch to ring a bell if some (long) scripts have finished or want to talk to you.
withsound = False

# A switch to tell if you want pngs to be transformed into jpg
makejpgarchives = True

# A switch to reduce the verbosity of the fortran MCS programs :
silencemcs = True


# Max number of CPU cores to use (0 = automatic, meaning that all available cores will be used) :
maxcores = 0
# Only some scripts run on multiple cores. It is noramlly fine to leave this on 0.
# You might want to use the manual setting for instance if someone is already using some cores for other jobs etc. 

#------------------------ IMPORTATION --------------------------------------

# The "set name" of the images you want to add to the database
# Could for example reflect the telescope ...

setname = "1"
telescopename = "Mercator"
# Available telescopenames :
# Mercator, EulerC2, EulerCAM, HCT, SMARTSandicam, Liverpool
# MaidanakSITE, MaidanakSI
# HoLi, NOTalfosc, skysim, NOHEADER
# where NOHEADER is a special name to not read any header information from the FITS files.
# where Combi is a scecial name to read the header of the combined images.
# where skysim is a scecial name to read the header of the simulated images.

# Where are these images ?
rawdir = "/home/epfl/eulaers/unsaved/prered_Mercator/reduc/J1001+5027_RG_crop"
# Remember that these images should be prereduced and have clean borders (cut pre/overscan) !
# Also they should be in a coherent "orientation" (rotations are ok, but no mirror flips).

#------------------------ ASTROCALC ----------------------------------------

# a string (format = "Xephem"-like catalog entry) specifing the target coordinates.
# In this case, we have : name, f|Q = fixed quasar, RA (H:M:S), Dec (D:M:S), mag, epoch
# This is used for the astronomical calculations (mainly HJD).

#xephemlens = "J1001+5027,f|Q,10:01:28.61,50:27:56.90,19.0,2000"
#xephemlens = "HS2209+1914,f|Q,22:11:30.30,19:29:12.00,19.0,2000"
#xephemlens = "UCAC2_14535478,f|Q,1:25:15.40,-40:08:22.00,19.0,2000" # Euler test field taken 2009-11-04
#xephemlens = "H1413+117,f|Q,14:15:46.40,+11:29:41.40,19.0,2000"
#xephemlens = "HE0047-1756,f|Q,00:50:27.83,-17:40:08.80,19.0,2000"
#xephemlens = "J1226-0006,f|Q,12:26:08.02,-00:06:02.20,19.0,2000"
#xephemlens = "RXJ1131-123,f|Q,11:31:55.40,-12:31:55.00,19.0,2000"
#xephemlens = "PG1115+080,f|Q,11:18:17.00,+07:45:57.70,19.0,2000"
#xephemlens = "Q1355-2257,f|Q,13:55:43.38,-22:57:22.90,19.0,2000"
#xephemlens = "Q2237+030,f|Q,22:40:30.34,+03:21:28.80,19.0,2000"
#xephemlens = "RXJ1131-123,f|Q,11:31:55.40,-12:31:55.00,19.0,2000"
#xephemlens = "UM673,f|Q,01:45:16.59,-09:45:17.30,19.0,2000"
#xephemlens = "J1650+425,f|Q,16:50:43.44,+42:51:45.00,19.0,2000"
#xephemlens = "J1330+1810,f|Q,13:30:18.65,+18:10:32.15,19.0,2000"
#xephemlens = "SBS1520+530,f|Q,15:21:44.83,+52:54:48.6,17.61,2000"
#xephemlens = "SDSS1004+4112,f|Q,10:04:34.91,+41:12:42.8,17.53,2000"
#xephemlens = "SDSS1029+2623,f|Q,10:29:13.35,+26:23:31.8,18.8,2000"
#xephemlens = "SDSS1206+4332,f|Q,12:06:29.64,+43:32:17.59,18.95,2000"
#xephemlens = "SDSS0819+5356,f|Q,08:19:59.79,+53:56:24.3,19.9,2000"
#xephemlens = "SDSS1400+3134,f|Q,14:00:12.77,+31:34:54.1,19.4,2000"
#xephemlens = "J0158-4325,f|Q,01:58:41.44,-43:25:04.19,19.0,2000"
#xephemlens = "HS0818+1227,f|Q,08:21:39.10,+12:17:29.00,19.0,2000"
#xephemlens = "HE2149-274,f|Q,21:52:07.44,-27:31:50.19,19.0,2000"
#xephemlens = "WFI2033-4723,f|Q,20:33:42.08,-47:23:43.00,20.0,2000"
xephemlens = "Simulation,f|Q,00:00:00.00,+00:00:00.0,20.0,2000"

# Now you can run all the scripts until the alignment !

#------------------------ ALIGNMENT ----------------------------------------

# reference image name (for alignment and deconvolution) :

refimgname = "1_093307_RG_J1001+5027"

# dimensions you want for the aligned images (you have to start at pixels (1,1), no choice)
dimx = 2000
dimy = 2000
# currently this is used only in the stupid geomap, to make the transform valid
# for the full frame.

# Where is the lens ?
lensregion = "[871:911,969:1006]"
# Region of empty sky (to estimate stddev), 100 x 100 pixel is more then enough.
emptyregion = "[800:1000,350:550]"
# These regions apply to the aligned images.

# And now some alignment parameters that you should actually not have to change at all.

# Tolerance in pixels when identifying stars and finding the transformation.
identtolerance = 5.0
# 5.0 should work (even 2.0 does), higher values would be required in case of strong distortion.

identminnbrstars = 5
# number of stars that must match for the finding to be sucessfull
# a default value would be half of the number of alignment stars for instance.
# minimum is 3 of course. 5 is fine, it will work well in nearly all cases.
# A small number will give higher probability of wrong alignment

identfindmindist = 300
# distances (in pixels) of stars to consider for finding pairs in the algorithm
# 300 pixels is good. Put smaller values if you have only a few close stars available for alignment.



#------------------------ SEXTRACTOR PHOTOMETRY READOUT --------------------

sexphotomname = "sexphotom1"	# No need to touch this, same for the fields below.

# Fields you want in the database. Not restricted to photometry, you could add any fields.
# Note the convention : if you ask sextractor for 3 apertures, those fields will be named
# FLUX_APER, FLUX_APER1, FLUX_APER2 (this is done by astroasciidata, not by sextractor)
# Do not forget to update both default.sex and default.param if you want to make changes to
# the apertures.

sexphotomfields = [
{"sexname":"FLUX_AUTO", "dbname":"auto_flux", "type":"float"},
{"sexname":"FLUX_APER", "dbname":"ap20_flux", "type":"float"},
{"sexname":"FLUX_APER1", "dbname":"ap30_flux", "type":"float"},
{"sexname":"FLUX_APER2", "dbname":"ap60_flux", "type":"float"},
{"sexname":"FLUX_APER3", "dbname":"ap90_flux", "type":"float"},
{"sexname":"FLUX_APER4", "dbname":"ap120_flux", "type":"float"}
]

#------------------------ DEEP FIELD COMBINATION (FACULTATIVE) -------------

# Choose a plain name for your combination (like for instance "1" for your first try...)
combibestname = "best1"

combibestmaxseeing = 1.3 	# Maximum seeing, in arcseconds
combibestmaxell = 0.1 		# Maximum ellipticity (field "ell")
combibestmaxmedcoeff = 1.2	# Maximum medcoeff (ref image has 1.0)
combibestmaxstddev = 20.0 	# Maximum sky stddev, in ADU

#------------------------ IMAGE STACKING (FACULTATIVE) ---------------------

#Choose a name for your combination. It should reflect the normalization coeff that your using ('medcoeff' or 'renormabc1' if you computed some new one)
# Suggestion for names : 'medcoeff1' for your first try using the medcoeff
combiname = "medcoeff1"

renormcoeff = 'medcoeff'	# you can choose which coeff you want to use for the combination


#------------------------ PSF CONSTRUCTION ---------------------------------

# Choose a name for your PSF. Has to be done before running any PSF script.
# Make it short, and if possible reflect the choice of stars (like "abc" if you use stars a, b, and c)
# Also, you will want it to reflect wich version of PSF you want to use. So please,
# put "new" somewhere in the string if you want use the new psf, and "old" otherwise.
# Suggestion for names : "newabcd1" for your first try using stars a, b, c and d...

psfname = "pyMCSabcd1"	

# The otherway round, do not put "new" in that string if you build your PSF with the old codes !
# This is not used to switch the programs automatically, but to recognize which PSF was used afterwards.

# General remark : such names will be used in filenames... no funny symbols or spaces please !


# Sensitivity of cosmic ray detection. Lower values = more sensitive = more detections
# A good conservative default is 5.0 . So 4.0 would be a bit more sensitive. Check that you do not mask noise ...
cosmicssigclip = 6.0

#------------------------ OBJECT EXTRACTION --------------------------------

objname = "lens"	# Give a name to the object you want to extract.
			# Typically, "a" if you extract star "a", and
			# "lens" if you extract the lens ...
			# If you want to play with different cosmics or so, there
			# is no problem to extract the same object under different
			# names !


#------------------------ DECONVOLUTION ------------------------------------

decname = "full"		# Choose a name for your deconvolution. No need to reflect the source. Examples : "full", "test"

decobjname = "lens"		# Select which object you want to deconvolve : give an existing objname.
				# You don't have to set the objname in the "OBJECT EXTRACTION" section.

decnormfieldname = "medcoeff"	# The normalization coefficient to apply to the image prior to deconv.
				# "None" is special, it means a coeff of 1.0 for every image.
				# The name of the default sextractor photometry is "medcoeff"
				# If you choose a renormalization, give an existing renormname.


decpsfnames = ["abce1"]		# The PSF(s) you want to use : give one or more psfnames in form of a list.
				# The first psfname has the lowest priority.


#------------------------ RENORMALIZATION ----------------------------------

renormname = "renormabc1"	# Choose a name for the new renormalization coefficient
				# (something that reflects the sources... like "renormabc")
				# Make it short ... but start it with the letters renorm

# Which sources do you want to use for the renormalization (give (deckey, sourcename) ):
renormsources = [
('dec_full_a_medcoeff_abce1', 'a'),
('dec_full_b_medcoeff_abce1', 'b'),
('dec_full_c_medcoeff_abce1', 'c')
]

# You can than change these before running 2_plot_star_curves_NU.py, to get curves for other stars.

#------------------------ PLOTS ETC ----------------------------------------

plotnormfieldname = None	# Used only for the quicklook plots, after the deconvolution :
				# None -> we normalize with the coeffs used for the deconvolution.
				# renormname -> we use these coeffs instead. Allows for a first check.
				# Note that this does NOT affect the content of the database in any way !


#---------------------------------------------------------------------------


