#---------------------------------------------------------------------------


# The "working" dir where all the pipeline products will be *written*
# ("big-old-never-backuped-disk")
workdir = "/Users/martin/Desktop/lc_run/run/RXJ1131_ECAM"


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
makejpgarchives = False

# A switch to reduce the verbosity of the fortran MCS programs :
silencemcs = True

# A switch to tell the scripts that you are running an update with the existing settings.
# To be set to true ONLY if you work in all_update_scripts !!
update = False

#If you want only your test sample whan checking the png :
sample_only = True


# Max number of CPU cores to use (0 = automatic, meaning that all available cores will be used) :
maxcores = 0
# Only some scripts run on multiple cores. It is noramlly fine to leave this on 0.
# You might want to use the manual setting for instance if someone is already using some cores for other jobs etc. 

#------------------------ IMPORTATION --------------------------------------

# The "set name" of the images you want to add to the database
# Could for example reflect the telescope ...

setname = "3"
telescopename = "EulerCAM"
# Available telescopenames :
# Mercator, EulerC2, EulerCAM, HCT, SMARTSandicam, Liverpool
# MaidanakSITE (for 2030x800), MaidanakSI (for 4096x4096), Maidanak2k2k (for 2084 x 2084)
# HoLi, NOTalfosc, skysim, NOHEADER
# where NOHEADER is a special name to not read any header information from the FITS files.
# where Combi is a scecial name to read the header of the combined images.
# where skysim is a scecial name to read the header of the simulated images.

# Where are these images ?
rawdir = "/Users/martin/Desktop/lc_run/data_raw/"
# Remember that these images should be prereduced and have clean borders (cut pre/overscan) !
# Also they should be in a coherent "orientation" (rotations are ok, but no mirror flips).

#------------------------ ASTROCALC ----------------------------------------

# a string (format = "Xephem"-like catalog entry) specifing the target coordinates.
# In this case, we have : name, f|Q = fixed quasar, RA (H:M:S), Dec (D:M:S), mag, epoch
# This is used for the astronomical calculations (mainly HJD).

#xephemlens = "J1349+1227,f|Q,13:49:29.84,+12:27:06.88,20.0,2000" #that one is new, not sure about the mag...
#xephemlens = "J0924+0219,f|Q,09:24:55.87,+02:19:24.9,19.0,2000" # same here
#xephemlens = "J0246-0825,f|Q,02:46:34.11,-08:25:36.20,20.0,2000"
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
#xephemlens = "RXJ1131-123,f|Q,11:31:51.50,-12:31:58.70,19.0,2000"
#xephemlens = "UM673,f|Q,01:45:16.59,-09:45:17.30,19.0,2000"
#xephemlens = "J1650+425,f|Q,16:50:43.44,+42:51:45.00,19.0,2000"
#xephemlens = "J1330+1810,f|Q,13:30:18.65,+18:10:32.15,19.0,2000"
#xephemlens = "J1332+0347,f|Q,13:32:22.62,+03:47:39.90,20.0,2000"
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
#xephemlens =  "J1335+0118,f|Q,13:35:34.79,+01:18:05.50,20.0,2000"
#xephemlens = "J0832+0404,f|Q,08:32:17.00,+04:04:05.20,20.0,2000"
#xephemlens = "J1322+1052,f|Q,13:22:36.42,+10:52:39.43,20.0,2000"
#xephemlens = "HE0435-1223,f|Q,04:38:14.90,-12:17:14.40,19.0,2000"
# xephemlens = "WFI2026-4536,f|Q,20:26:10.45,-45:36:27.10,15.9,2000"
xephemlens = "HE1104-1805,f|Q,11:06:33.39,-18:21:23.80,19.0,2000"
#xephemlens = "Simulation,f|Q,00:00:00.00,+00:00:00.0,20.0,2000"

# Now you can run all the scripts until the alignment !

#------------------------ ALIGNMENT ----------------------------------------

# do you want to work on defringed images (if they exists ?)
if telescopename == "WFI":
    defringed = True
else :
    defringed = False

# reference image name (for alignment and deconvolution) :

refimgname = "3_ECAM.2011-08-31T09:35:49.000"

# dimensions you want for the aligned images (you have to start at pixels (1,1), no choice)
if telescopename == "WFI":
    dimx = 2022
    dimy = 4000
else :
    dimx = 3600
    dimy = 3600
# currently this is used only in the stupid geomap, to make the transform valid
# for the full frame.

# Where is the lens ?
lensregion = "[1459:1497,1809:1844]"
# Region of empty sky (to estimate stddev), 100 x 100 pixel is more then enough.
emptyregion = "[1383:1513,1676:1745]"
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
{"sexname":"FLUX_APER4", "dbname":"ap120_flux", "type":"float"},
{"sexname":"FLUXERR_AUTO", "dbname":"auto_flux_err", "type":"float"},
{"sexname":"FLUXERR_APER", "dbname":"ap20_flux_err", "type":"float"},
{"sexname":"FLUXERR_APER1", "dbname":"ap30_flux_err", "type":"float"},
{"sexname":"FLUXERR_APER2", "dbname":"ap60_flux_err", "type":"float"},
{"sexname":"FLUXERR_APER3", "dbname":"ap90_flux_err", "type":"float"},
{"sexname":"FLUXERR_APER4", "dbname":"ap120_flux_err", "type":"float"}
]

#------------------------ DEEP FIELD COMBINATION (FACULTATIVE) -------------

# Choose a plain name for your combination (like for instance "1" for your first try...)
combibestname = "best1"

combibestmaxseeing = 1.4 	# Maximum seeing, in arcseconds
combibestmaxell = 0.18 		# Maximum ellipticity (field "ell")
combibestmaxmedcoeff = 1.25	# Maximum medcoeff (ref image has 1.0)
combibestmaxstddev = 80.0 	# Maximum sky stddev, in ADU

#------------------------ IMAGE STACKING (FACULTATIVE) ---------------------

#Choose a name for your combination. It should reflect the normalization coeff that your using ('medcoeff' or 'renormabc1' if you computed some new one)
# Suggestion for names : 'medcoeff1' for your first try using the medcoeff
combinightname = "medcoeff1"

combinightrenormcoeff = 'medcoeff'	# you can choose which coeff you want to use for the combination


#------------------------ PSF CONSTRUCTION ---------------------------------

# Choose a name for your PSF. Has to be done before running any PSF script.
# Make it short, and if possible reflect the choice of stars (like "abc" if you use stars a, b, and c)
# Also, you will want it to reflect wich version of PSF you want to use. So please,
# put "new" somewhere in the string if you want use the new psf, and "old" otherwise.
# Suggestion for names : "newabcd1" for your first try using stars a, b, c and d...

psfname = "abcdef"

# The otherway round, do not put "new" in that string if you build your PSF with the old codes !
# This is not used to switch the programs automatically, but to recognize which PSF was used afterwards.

# General remark : such names will be used in filenames... no funny symbols or spaces please !


# Sensitivity of cosmic ray detection. Lower values = more sensitive = more detections
# A good conservative default is 5.0 . So 4.0 would be a bit more sensitive. Check that you do not mask noise ...
cosmicssigclip = 6.0


# Remove saturated images. A maxpixelvaluecoeff of X means that the images where the psf stars have a pixel with a value higher than saturlevel*gain*X are indicated and can be disregarded after the PSF construction. Typically, for a cut at 50k (with saturation at 64k), use maxpixelvaluecoeff = 0.78

maxpixelvaluecoeff = 0.78

#------------------------ OBJECT EXTRACTION --------------------------------

objname = "a"	# Give a name to the object you want to extract.
			# Typically, "a" if you extract star "a", and
			# "lens" if you extract the lens ...
			# If you want to play with different cosmics or so, there
			# is no problem to extract the same object under different
			# names !

objnames = ["lens", "a","b","c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o","p", "q", "r", "s", "t", "u", "v", "w","x","y", "z"]
			# As above, but all extractions are performed in a single scrip
			# 12_all_extrnancosm.py
			# More efficient on some configurations (like if IO flow is limited)

#------------------------ DECONVOLUTION ------------------------------------

decname = "noback"		# Choose a name for your deconvolution. No need to reflect the source. Examples : "full", "test"

decobjname = "lens"		# Select which object you want to deconvolve : give an existing objname.
				# You don't have to set the objname in the "OBJECT EXTRACTION" section.

decnormfieldname = "medcoeff"	# The normalization coefficient to apply to the image prior to deconv.
				# "None" is special, it means a coeff of 1.0 for every image.
				# The name of the default sextractor photometry is "medcoeff"
				# If you choose a renormalization, give an existing renormname.


decpsfnames = ["abcdef"]		# The PSF(s) you want to use : give one or more psfnames in form of a list.
				# The first psfname has the lowest priority.

makeautoskiplist = True  # Do you want the automatic update scripts to rerun the autoskiplist script or not ?

#------------------------ RENORMALIZATION ----------------------------------

renormname = "renorm_all"	# Choose a name for the new renormalization coefficient
				# (something that reflects the sources... like "renormabc")
				# Make it short ... but start it with the letters renorm

# Which sources do you want to use for the renormalization (give (deckey, sourcename) ):
# NEW : the FIRST one of the sources below will be used as a reference to scale the coeffs between different telescopes !
renormsources = [
('dec_noback_a_medcoeff_abcdef', 'a'),
('dec_noback_b_medcoeff_abcdef', 'b'),
('dec_noback_c_medcoeff_abcdef', 'c'),
('dec_noback_d_medcoeff_abcdef', 'd'),
('dec_noback_e_medcoeff_abcdef', 'e'),
('dec_noback_f_medcoeff_abcdef', 'f'),
('dec_noback_g_medcoeff_abcdef', 'g'),
('dec_noback_h_medcoeff_abcdef', 'h'),
('dec_noback_i_medcoeff_abcdef', 'i'),
('dec_noback_j_medcoeff_abcdef', 'j'),
('dec_noback_k_medcoeff_abcdef', 'k'),
('dec_noback_l_medcoeff_abcdef', 'l'),
('dec_noback_m_medcoeff_abcdef', 'm'),
('dec_noback_n_medcoeff_abcdef', 'n'),
('dec_noback_o_medcoeff_abcdef', 'o'),
('dec_noback_p_medcoeff_abcdef', 'p'),
('dec_noback_q_medcoeff_abcdef', 'q'),
('dec_noback_r_medcoeff_abcdef', 'r'),
('dec_noback_s_medcoeff_abcdef', 's'),
('dec_noback_t_medcoeff_abcdef', 't'),
('dec_noback_u_medcoeff_abcdef', 'u'),
('dec_noback_v_medcoeff_abcdef', 'v'),
('dec_noback_w_medcoeff_abcdef', 'w'),
('dec_noback_x_medcoeff_abcdef', 'x'),
('dec_noback_y_medcoeff_abcdef', 'y'),
('dec_noback_z_medcoeff_abcdef', 'z')
]

# You can than change these before running 2_plot_star_curves_NU.py, to get curves for other stars.

#------------------------ PLOTS ETC ----------------------------------------

plotnormfieldname = None	# Used only for the quicklook plots, after the deconvolution :
				# None -> we normalize with the coeffs used for the deconvolution.
				# renormname -> we use these coeffs instead. Allows for a first check.
				# Note that this does NOT affect the content of the database in any way !

lc_to_sum = None #used in quicklooks by night
                # None --> will plot all the available lightcurves
                # ['A','D'] --> sum the two entry given in a list

#---------------------------------------------------------------------------


