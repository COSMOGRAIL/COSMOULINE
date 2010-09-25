#------------------------------------------------------------------------------------------------------------------


# The "working" dir where all the pipeline products will be *written*
# ("big-old-never-backuped-disk")
workdir = "/home/epfl/eulaers/unsaved/cosmouline_work/J1001"


#------------------------ Switches -----------------------------------


# A switch to tell if these testlist-flags should be used.
# If these flags are set, the scripts will run only on your subset of images.
thisisatest = False

# A switch to use soft links instead of true file copies whenever possible (you might not want this for some reasons)
uselinks = True

# A switch to make all scripts skip any questions
askquestions = True

# A switch to display image by image plots that are normally not needed. If True, the database will not be updated !
# You should typically use this in connection with thisisatest = True ...
checkplots = False
	# This is used by : 1_character_scripts/4_skystats.py, 3b_measureseeing.py

# A switch to ring a bell if some (long) scripts have finished or want to talk to you.
withsound = True

# A switch to tell if you want pngs to be transformed into jpg
makejpgarchives = True

# A switch to reduce the verbosity of the fortran MCS programs :
silencemcs = False


#------------------------- import new images  ---------------------------------------------------------------

# The "set name" of the images you want to add to the database
# Could for example reflect the telescope ...

setname = "Mer1"
telescopename = "Mercator"
# names : Mercator, Euler, HCT, MaidanakSITE, MaidanakSI, MaidanakPeltier, HoLi, NOTalfosc, NOHEADER
# where NOHEADER is a special name to not read any header information from the FITS files.

# Where are these images ?
rawdir = "/home/epfl/eulaers/unsaved/prered_Mercator/reduc/J1001+5027_RG_crop"
# Remember that these images should be prereduced and have clean borders (cut pre/overscan) !
# Also they should be in a coherent "orientation" (rotations are ok, but no mirror flips).

#-------------------------------- astrocalc --------------------------------------------------------------------

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
xephemlens = "J1330+1810,f|Q,13:30:18.65,+18:10:32.15,19.0,2000"

# Now you can run all the srcipts until the alignment !

#---------------------------- alignment and stats -----------------------------------------------------------------

# reference image name (for alignement and deconvolution) :

refimgname = "Mer1_093307_RG_J1001+5027"

# dimensions you want for the aligned images (you have to start at pixels (1,1), no choice)
dimx = 2000
dimy = 2000
# currently this is used only in the stupid geomap, to make the transform valid
# for the full frame.

# small region around the lens (as small as possible without loosing flux)
lensregion = "[871:911,969:1006]"
# region of empty sky (to estimate stddev etc)
emptyregion = "[1005:1105,1000:1100]"
# these regions apply to the aligned images (ie the reference) !




#----------------------------- facultative combination of some images -----------------------------

# Choose a plain name for your combination (like for instance "1" for your first try...)
combibestname = "best1"

combibestmaxseeing = 1.3 	# Maximum seeing, in arcseconds
combibestmaxell = 0.1 		# Maximum ellipticity (field "ell")
combibestmaxmedcoeff = 1.2	# Maximum medcoeff (ref image has 1.0)
combibestmaxstddev = 20.0 	# Maximum sky stddev, in ADU




#------------------------ PSF CONSTRUCTION ---------------------------------

# Choose a name for your PSF. Has to be done before running any PSF script.
# Make it short, and if possible reflect the choice of stars (like "abc" if you use stars a, b, and c)
# Also, you will want it to reflect wich version of PSF you want to use. So please,
# put "new" somewhere in the string if you want use the new psf, and "old" otherwise.
# Suggestion for names : "newabcd1" for your first try using stars a, b, c and d...

psfname = "defg1"	

# The otherway round, do not put "new" in that string if you build your PSF with the old codes !
# This is not used to switch the programs automatically, but to recognize which PSF was used afterwards.

# General remark : such names will be used in filenames... no funny symbols or spaces please !


# Sensitivity of cosmic ray detection. Lower values = more sensitive = more detections
# A good conservative default is 5.0 . So 4.0 is a bit more sensitive. Check that you do not mask noise ...
cosmicssigclip = 4.0

# Max number of CPU cores to use (0 = automatic, meaning that all available cores will be used)
# It is fine to leave this on 0.
# You might want to use the manual setting for instance if someone is already using some cores for other jobs etc. 
maxcores = 0
	# This is used by the multicpu PSF construction



#------------------------ OBJECT EXTRACTION --------------------------------

objname = "s"	# Give a name to the object you want to extract.
			# Typically, "a" if you extract star "a", and
			# "lens" if you extract the lens ...
			# If you want to play with different cosmics or so, there
			# is no problem to extract the same object under different
			# names !


#------------------------ DECONVOLUTION ------------------------------------

decname = "full"		# YES WE CAN !

decobjname = "lens"		# here you choose which object you want to deconvolve : give an existing objname.
				# You don't have to set the objname in the "OBJECT EXTRACTION" section.

decpsfnames = ["abce1"]	# here you choose the PSF(s) you want to use : give one or more psfnames in form of a list.
				# The first psfname has the lowest priority

decnormfieldname = "abce1"	# Give the name of the normalization coefficient to apply to the image prior to deconv.
				# "None" is special, it means a coeff of 1.0 for every image.
				# The name of the default sextractor photometry is "medcoeff"
				# If you choose a renormalization, give an existing renormfieldname 


#------------------------ RENORMALIZATION -----------------------------------


# a name for the new renormalization coefficient
# (your could choose something that reflects the sources... like "renormabc")
# Make it short ...

renormname = "abce1"

# which sources do you want to use for the renormalization (give (deckey, sourcename) ):
renormsources = [('dec_full_a_medcoeff_abce1', 'a'), ('dec_full_b_medcoeff_abce1', 'b'), ('dec_full_c_medcoeff_abce1', 'c'), ('dec_full_e_medcoeff_abce1', 'e')]

#---------------------------------------------------------------------------






