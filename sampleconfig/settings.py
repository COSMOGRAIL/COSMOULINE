from os.path import join
#----------------------- GENERAL INFO --------------------------------------
# this is mainly used in the export part, and when calculating 
# the distance to the moon, altitude of the sun, etc.
lensName = "PSJ0030-1525"
# here you can be more precise if you want:
lensRA   = "00:30:00.00"
lensDEC  = "-15:25:00.00"
# an estimate of the magnitude, not too important:
lensMag  = 19.0

#---------------------------------------------------------------------------


# The "working" dir where all the pipeline products will be *written*
# ("big-old-never-backuped-disk")
workdir = "/scratch/COSMOULINE/WFI_PSJ0030-1525/"

#------------------------ SWITCHES -----------------------------------------

# A switch to tell if these testlist-flags should be used.
# If these flags are set, the scripts will run only on your subset of images.
thisisatest = False
# A switch to use soft links instead of true file copies whenever possible 
# (you might not want this for some reasons)
uselinks = True
# A switch to make all scripts skip any questions
askquestions = False
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
sample_only = False
# Max number of CPU cores to use (0 = automatic, meaning that all available cores will be used) :
maxcores = 7
# Only some scripts run on multiple cores. It is noramlly fine to leave this on 0.
# You might want to use the manual setting for instance if someone is already using some cores for other jobs etc. 

#------------------------ IMPORTATION --------------------------------------
telescopename = "WFI"
# Available telescopenames :
# Mercator, EulerC2, EulerCAM, HCT, SMARTSandicam, Liverpool
# MaidanakSITE (for 2030x800), MaidanakSI (for 4096x4096), Maidanak2k2k (for 2084 x 2084)
# HoLi, NOTalfosc, skysim, NOHEADER
# where NOHEADER is a special name to not read any header information from the FITS files.
# where Combi is a scecial name to read the header of the combined images.
# where skysim is a scecial name to read the header of the simulated images.

# we import by setname.
# usually, we will set a setname by band.
# in this example we only have one setname or filter (filter id 844 of WFI)
# but you can add more. 
setnames = ["844"]

# Where are these images ?
baseraw = "/scratch/COSMOULINE/WFI_PSJ0030-1525/raw_dir/"

# usually, I keep each band in separate directories like this:
rawdirs = [join(baseraw, setname) for setname in setnames]
# feel free to change it to match your convention.

# Remember that these images should be prereduced 
# and have clean borders (cut pre/overscan) !
# Also they should be in a coherent "orientation" 
# (rotations are ok, but no mirror flips).

# USEFUL FOR VLT OR WFI images, which are HUGE.
# during copy convert, will trim this many lines
# from the top and the bottom.
# e.g., if trim_vertical = 1000:
# init height: 4000, final height: 2000
# shape (2000, 4000) --> shape (2000, 2000)
trim_vertical = 0
trim_horizontal = 0
# set to zero to not use.
if trim_vertical > 0 and telescopename not in ['WFI', 'VST']:
    raise RuntimeError("Are you sure you want to trim vertically??? comment me out if yes.")
if trim_horizontal > 0:
    raise RuntimeError("Are you sure you want to trim horizontally??? comment me out if yes.")

#------------------------ ASTROCALC ----------------------------------------
# a string (format = "Xephem"-like catalog entry) 
# specifing the target coordinates.
# In this case, we have : 
#       name, f|Q = fixed quasar, RA (H:M:S), Dec (D:M:S), mag, epoch
# This is used for the astronomical calculations (mainly HJD).
# MORE IMPORTANTLY, THIS IS BUILT AUTOMATICALLY FROM THE GENERAL INFO SECTION
# ABOVE.
xephemlens = f"{lensName},f|Q,{lensRA},{lensDEC},{lensMag:.01f},2000"

# Now you can run all the scripts until the alignment !

#------------------------ ALIGNMENT ----------------------------------------
# reference image name (for alignment, single one for all bands) :
refimgname = "844_WFI.2021-09-10T04:53:56.457"

# photometric and PSF reference images (one per band!)
refimgname_per_band = {"844": "844_WFI.2021-09-10T04:53:56.457"}

#------------------------ DEEP FIELD COMBINATION (FACULTATIVE) -------------

# Choose a plain name for your combination 
# (like for instance "1" for your first try...)
combibestname = "best1"
# aim for a combination that give ~ 50 images, as we load all of them
# in memory when combining them. 
combibestmaxseeing = 0.8 	 # Maximum seeing, in arcseconds
combibestmaxell = 0.1 		 # Maximum ellipticity (field "ell")
combibestmaxmedcoeff = 1.25  # Maximum medcoeff (ref image has 1.0)
combibestmaxstddev = 80.0 	 # Maximum sky stddev, in ADU

#------------------------ IMAGE STACKING (FACULTATIVE) ---------------------

# Choose a name for your combination. It should reflect the normalization coeff 
# that you're using ('medcoeff' or 'normabc1' if you computed some new one)
# Suggestion for names : 'medcoeff1' for your first try using the medcoeff
combinightname = "medcoeff1"

# you can choose which coeff you want to use for the combination
combinightnormcoeff = 'medcoeff'	


#------------------------ PSF CONSTRUCTION ---------------------------------

# Choose a name for your PSF. Has to be done before running any PSF script.
# Make it short, and if possible reflect the choice of stars 
# (like "abc" if you use stars a, b, and c)
# Also, you will want it to reflect wich version of PSF you want to use. So please,
# put "new" somewhere in the string if you want use the new psf, and "old" otherwise.
# Suggestion for names : "newabcd1" for your first try using stars a, b, c and d...
# THESE ARE TAKEN FROM YOUR normstars.cat CATALOGUE BUILT IN 4_norm_scripts!
psfname = "abijlt"

stampsize = 8.0  # arcsecond
subsampling_factor = 2

# create a summary plot for each image as we build the psfs
dopsfplots = True


# The otherway round, do not put "new" in that string
# if you build your PSF with the old codes !
# This is not used to switch the programs automatically,
# but to recognize which PSF was used afterward.

# General remark : such names will be used in filenames...
# no funny symbols or spaces please !

# Sensitivity of cosmic ray detection. 
# Lower values = more sensitive = more detections
# A good conservative default is 5.0 . 
# So 4.0 would be a bit more sensitive. Check that you do not mask noise ...
cosmicssigclip = 6.0


# Remove saturated images. A maxpixelvaluecoeff of X means that the images
#  where the psf stars have a pixel with a value higher than saturlevel*gain*X 
# are indicated and can be disregarded after the PSF construction. 
# Typically, for a cut at 50k (with saturation at 64k),
# use maxpixelvaluecoeff = 0.78

maxpixelvaluecoeff = 0.78
#-------------------------- NORMALIZATION ----------------------------------

# Choose a name for the new normalization coefficient:
normname = "norm_acd"

norm_stars = normname.split('_')[1]
# (something that reflects the sources... like "normabc")
# Make it short ... but start it with the letters norm

# Which sources do you want to use for the normalization
# (give (deckey, sourcename) ):
# NEW : the FIRST one of the sources below will be used as a reference
# to scale the coeffs between different telescopes!
psftouse = 'abijlt'
normsources = [
   [
    (f'dec_{setname}_noback_{starname}_None_{psftouse}', starname)
       for starname in norm_stars
   ] for setname in setnames
]

# You can than change these before running 2_plot_star_curves_NU.py,
# to get curves for other stars.


#------------------------ DECONVOLUTION ------------------------------------
# Choose a name for your deconvolution. No need to reflect the source.
# Examples : "full", "test"
decname = "full"

# Select which object you want to deconvolve : give an existing objname.
decobjname = "lens"		
# You don't have to set the objname in the "OBJECT EXTRACTION" section.

# The normalization coefficient to apply to the image prior to deconv:
decnormfieldname = "norm_1"	
# "None" is special, it means a coeff of 1.0 for every image.
# The name of the default sextractor photometry is "medcoeff"
# If you choose a normalization, give an existing normname.

# The PSF(s) you want to use : give one or more psfnames in form of a list.
decpsfnames = ["abijlt"]
# The first psfname has the lowest priority.


# Do you want the automatic update scripts to rerun the 
# autoskiplist script or not ?
makeautoskiplist = True  

# this will produce one deconvolution by object, by decname, by 
# normalisation, by psfname, and by setname. 
# in particular, you do not have to specify it here, but for a given
# set of parameters defined here there will be e.g. 4 deconvolutions
# happening at once if you have 4 setnames. 

# name of your point sources in order:
pointsourcesnames = ['A', 'B', 'C', 'D']

#------------------------ PLOTS ETC ----------------------------------------

plotnormfieldname = None#"norm_bdfghijlnop"
# Used only for the quicklook plots, after the deconvolution :
# None -> we normalize with the coeffs used for the deconvolution.
# normname -> we use these coeffs instead. Allows for a first check.
# Note that this does NOT affect the content of the database in any way !



lc_to_sum = None 
# used in quicklooks by night
# None --> will plot all the available lightcurves
# ['A','D'] --> sum the two entry given in a list

#---------------------------------------------------------------------------

#----------------------------  EXPORT PART ---------------------------------

# This section contains the configuration that will be used to convert the
# exported cosmouline database pkl into an rdb file ready for pycs.


# Name of the deconvolution (see the README file that comes with the db ...) :
deconvname = "dec_844_back1_lens_norm_1_abijlt"


################### Section for addfluxes.py ###########################

toaddsourcenames = [] # Name of the sources whose fluxes you want to add

sumsourcename = "A" # Name of the resulting source
# This new source will get added to the db as if had been made from a deconv.


################### Section for join.py ################################
# the general output name of the files is going to be (by default) the name
# of the lens:
outputname = lensName
# Name of the pointsources of this deconvolution :
sourcenames = ["A", "B"]

# Name of the normalization coeff to use :
normcoeffname = "norm_1"
# In principle it is also ok to put "medcoeff", as for the norm itself it works in the same way.
# Note : aside of the coefficients alone, we also read the fields (example) :
# normabcfg1_err	float, absolute error on the coeff
# normabcfg1_comment	string of ints, like "5" giving the number of stars for this coeff.

# Telescope- and set- names that you want to process "together" :
# Do not forget some image sets, check the README to see what you have in your db !
telescopenames = ["WFI"]
exportsetnames = ["844"]

# Narrow the range of images you want to use (images beyond these limits are disregarded,
# i.e., not included in the nights).
imgmaxseeing = 1.5
imgmaxell = 0.15
imgmaxrelskylevel = 10000.0 # In electrons, for a normalization of 1.0 (i.e. ref image)
imgmaxmedcoeff = 8.0

# Additionally, you can use a skiplist.
# Same "format" as for cosmouline, i.e. one imgname per line + facult comment.
# Example :
# 1_C2.2010-08-03T01:14:52.000     I don't like this one
# To use such a list, give the filename (not the full path) below, and put the file into 
# the lcmanipdir.

imgskiplistfilename = None
#imgskiplistfilename = "skiplist.txt"

# Narrow the range of nights you want to use (values are the medians among the images in a night).
# Nights beyond these limits are flagged, not removed !
nightmaxseeing = 5.0
nightmaxell = 0.95
nightmaxrelskylevel = 50000.0 # Skylevel in electrons, for a normalization of 1.0 (i.e. ref image)
nightmaxnormcoeff = 20.0
nightminnbimg = 3 # The minimal number of images within a night. Night flagged if number is below.


# Do you want me to write the usual 2 header lines into my rdb files ?
writeheader = True
# Do you want to see interactive plots (otherwise I save them to file) ?
showplots = True
