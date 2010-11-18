#---------------------------------------------------------------------------
# Sample configuration file for cosmouline.
# This file is under version control, don't tweak your settings here !
# Instead, copy me to config.py, and then edit config.py.
# config.py is excluded from svn.
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
# User settings :
#---------------------------------------------------------------------------

# Choose a computer :
computer = "obssr1"

# The pipeline dir that contains all the scripts (and this "config.py" ) :
pipedir = "/my/absolute/path/to/cosmouline/pipe_svn"

# The configuration directory that contains the configuration files :
# ("small-precious-frequently-backuped-disk")
# The scripts do only read, but never write, from here !
configdir = "/my/absolute/path/to/cosmouline/configs/config_HE0435"

#---------------------------------------------------------------------------
# All further settings are made into the configdir.
# You should normally not have to change other lines of this config.py
#---------------------------------------------------------------------------







import os
import shutil
import sys

# to get access to all our modules without installing anything :
sys.path.append(os.path.join(pipedir, "modules"))

# Read "global parameters" of the lens / deconvolution :
execfile(os.path.join(configdir, "settings.py"))

#----------------------- COMPUTER SETUP -----------------------------

#---------------------------------------------------------------------------
if computer=="maltemac":
	sex = "/Applications/sextractor/sex"
	#sex = "/usr/local/bin/sex"
#---------------------------------------------------------------------------
if computer=="obsds":
	sex = "nice -n 19 /scisoft/bin/sex"
#---------------------------------------------------------------------------
if computer=="obssr1":
	sex = "nice -n 19 /usr/bin/sex"
#---------------------------------------------------------------------------
if computer=="rathna":
	sex = "nice -n 19 /scisoft/bin/sex"
#---------------------------------------------------------------------------
if computer=="topaze":
	sex = "/usr/local/bin/sex"
#---------------------------------------------------------------------------

# Path to compiled programs :

mcsf77dir = os.path.join(pipedir, "progs", "MCSf77")

extractexe = "nice -n 19 " + os.path.join(mcsf77dir, "extract.exe") 
psfexe = "nice -n 19 " + os.path.join(mcsf77dir, "psf.exe") 
deconvexe = "nice -n 19 " + os.path.join(mcsf77dir, "deconv.exe") 
if silencemcs == True:
	psfexe = "nice -n 19 " + os.path.join(mcsf77dir, "psf_silence.exe") 
	deconvexe = "nice -n 19 " + os.path.join(mcsf77dir, "deconv_silence.exe") 



# Path to pyMCS :
# (not yet needed ...)
pymcsdir = "/Users/mtewes/Documents/Prog/Python/pyMCS/pyMCS_jan2010/"

#---------------------------------------------------------------------------


#------------------------ GENERAL CONFIG ---------------------------------


# The database of the images, fundamental for all scripts :
imgdb = os.path.join(workdir, "database.dat")	# This will be a nice KirbyBase.
dbbudir = os.path.join(workdir, "backups")		# The database is automatically backuped here.


alidir = os.path.join(workdir, "ali/")		# Alignment etc is done here
plotdir = os.path.join(workdir, "plots/")	# Some plots will go here

# Image lists (line format : imgname comment (you can leave blank lines and use "#" to comment a line !)) :

imgkicklist = os.path.join(configdir, "kicklist.txt")# Images that get "gogogo" set to False by the extrascript "kickimg.py",
							# as they simply cannot be used (too faint, cosmic on lens, etc)
							# No other script uses that list.

testlist = os.path.join(configdir, "testlist.txt")			# This is a "white list" for test runs (e.g. psf construction, ...).
							# Write images + comments on this list, and use the extrascript "set_testlist.py" to
							# set the "testlist" and "testcomment" flags in the database.
							# This list is also handy if you want to rebuild some handpicked psfs after 
							# a change of some parameters for instance !

# File with the alignment stars
alistarscat = os.path.join(configdir, "alistars.cat")

# File with the normalisation stars
normstarscat = os.path.join(configdir, "normstars.cat")

#------------------------ BEST IMAGE COMBINATION ---------------------------

combibestkey = "combi_" + combibestname

#------------------------ PSF CONSTRUCTION ---------------------------------

psfkey = "psf_" + psfname		# Don't touch (all this is hard-coded in the first dec prepfiles script !)
psfdir = os.path.join(workdir, psfkey)	# Don't touch
psfkeyflag = "flag_" + psfkey		# Don't touch
psfcosmicskey = psfkey + "_cosmics"	# Don't touch

psfstarcat = os.path.join(configdir, psfkey + ".cat")		# file with psf star coordinates (lineformat : "somename x y")
psfkicklist = os.path.join(configdir, psfkey + "_skiplist.txt")
				# Its a black list *after* the psf construction (i.e. that will be used for the deconvolution)
				# Note that this can potentially be read by various scripts : this is why
				# It is important to KEEP THIS LIST IN YOUR CONFIGDIR, FOR EVERY PSF, AND WITH THIS PRECISE NAME !


#------------------------ OBJECT EXTRACTION --------------------------------
	
objkey = "obj_" + objname		# Don't touch, it would screw more than you can think of ! (dec preparation + png + lookback + ...)
objdir = os.path.join(workdir, objkey)	# Don't touch, idem...
objkeyflag = "flag_" + objkey	# Don't touch
objcosmicskey = objkey + "_cosmics" # Don't touch

objcoordcat = os.path.join(configdir, objkey + ".cat")



#------------------------ DECONVOLUTION ------------------------------------

		# I like to do many deconvolutions... we could choose an explicit deckey like :
deckey = "dec_" + decname + "_" + decobjname + "_" + decnormfieldname + "_" + "_".join(decpsfnames)
		# Or, if you prefer, just use decname (but then you should write down what you did !)
#deckey = decname

ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")	# where the initial position and intensities are written
decskiplist = os.path.join(configdir, deckey + "_skiplist.txt")	# put here images that you do not want to include in this particular deconvolution.
deckeyfilenum = "decfilenum_" + deckey 				# the name of the field that contains 001, 002 etc
deckeypsfused = "decpsf_" + deckey 				# the name of the field to contain the used psfname for "this particular image"
deckeynormused = "decnorm_" + deckey				# the name of the field to contain the normalization coeff that was actually used
							# Don't even think of changing this last one (hard coded in : renorm)
decdir = os.path.join(workdir, deckey)				# where the deconvolution will be done



#------------------------ RENORMALZATION -----------------------------------

renormcommentfieldname = renormname + "_comment"


#---------------------------------------------------------------------------


# F77 MCS config files templates (no need to change anything here)

extract_template_filename = os.path.join(configdir, "template_extract.txt")
psf_template_filename = os.path.join(configdir, "template_psfmofsour8.txt")

#old_extract_template_filename = os.path.join(configdir, "old_extract_template.txt")
#old_psfm_template_filename = os.path.join(configdir, "old_psfmof_template.txt")
#old_lambda_template_filename = os.path.join(configdir, "old_lambda_template.txt")

in_template_filename = os.path.join(configdir, "template_in.txt")
deconv_template_filename = os.path.join(configdir, "template_deconv.txt")

#pyMCS_config_template_filename = os.path.join(configdir, "emplate_pyMCS.py")

#---------------------------------------------------------------------------


# check for some general dirs

if not os.path.isdir(pipedir):
	sys.exit("Your pipedir does not exist !")
if not os.path.isdir(configdir):
	sys.exit("Your configdir does not exist !")
if not os.path.isdir(workdir):
	sys.exit("Your workdir does not exist !")

if not os.path.isdir(alidir): 
	os.mkdir(alidir)
if not os.path.isdir(plotdir): 
	os.mkdir(plotdir)
if not os.path.isdir(dbbudir): 
	os.mkdir(dbbudir)

# not needed anymore since I tweaked KirbyBase :
# turn off deprecation warnings for KirbyBase (yes I know, this is SAD...)
#import warnings
#warnings.warn("deprecated", DeprecationWarning)
#warnings.simplefilter("ignore")


#---------------------------------------------------------------------------


