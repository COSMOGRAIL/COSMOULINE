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
computer = "martin"

# The pipeline dir that contains all the scripts (and this "config.Spy" ) :
pipedir = "/Users/martin/Desktop/COSMOULINE/pipe/"

# The configuration directory that contains the configuration files :
# ("small-precious-frequently-backuped-disk")
# The scripts do only read, but never write, from here !
configdir = "/Users/martin/Desktop/COSMOULINE/config/HE0435_ECAM/"

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
print os.path.join(configdir, "settings.py")
execfile(os.path.join(configdir, "settings.py"))

#----------------------- COMPUTER SETUP -----------------------------
if computer=="vivien":
	sex = "/bin/sex"
	#sex = "~/modules/ureka/Ureka/bin/sex"
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
if computer=="regor2":
	sex = "nice -n 19 /scisoft/bin/sex"
#---------------------------------------------------------------------------
if computer=="martin":
	sex = "/sw/bin/sex"
#---------------------------------------------------------------------------

# Path to compiled programs :

mcsf77dir = os.path.join(pipedir, "progs", "MCSf77")

if computer=="vivien":
	mcsf77dir = '/home/vivien/modules/MCSf77'


extractexe = "sudo nice -n 19 " + os.path.join(mcsf77dir, "extract.exe")
psfexe = "sudo nice -n 19 " + os.path.join(mcsf77dir, "psf.exe")
deconvexe = "sudo nice -n 19 " + os.path.join(mcsf77dir, "deconv.exe")
if silencemcs == True:
	psfexe = "sudo nice -n 19 " + os.path.join(mcsf77dir, "psf_silence.exe")
	deconvexe = "sudo nice -n 19 " + os.path.join(mcsf77dir, "deconv_silence.exe")

"""
oldpsfmcsf77dir = os.path.join(pipedir, "progs", "oldpsfMCSf77")
oldextractexe = "nice -n 19 " + os.path.join(oldpsfmcsf77dir, "extract.exe") 
oldpsfmexe = "nice -n 19 " + os.path.join(oldpsfmcsf77dir, "psfm.exe") 
oldpsfexe = "nice -n 19 " + os.path.join(oldpsfmcsf77dir, "psf-auto.exe") 
"""

#---------------------------------------------------------------------------


#------------------------ GENERAL CONFIG ---------------------------------


# The database of the images, fundamental for all scripts :
imgdb = os.path.join(workdir, "database.dat")	# This will be a nice KirbyBase.
dbbudir = os.path.join(workdir, "backups")	# The database is automatically backuped here.


alidir = os.path.join(workdir, "ali/")		# Alignment etc is done here
plotdir = os.path.join(workdir, "plots/")	# Some plots will go here (not used anymore)

# Image lists (line format : imgname comment (you can leave blank lines and use "#" to comment a line !)) :

imgkicklist = os.path.join(configdir, "kicklist.txt")	# Images that get "gogogo" set to False by the extrascript "kickimg.py",
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


#------------------------ COMBINATION BY NIGHT ------------------------------

combinightdirname = 'combinight_' +combinightname

combinightdirpath = os.path.join(workdir, combinightdirname)


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
# single extraction
objkey = "obj_" + objname		# Don't touch, it would screw more than you can think of ! (dec preparation + png + lookback + ...)
objdir = os.path.join(workdir, objkey)	# Don't touch, idem...
objkeyflag = "flag_" + objkey	# Don't touch
objcosmicskey = objkey + "_cosmics" # Don't touch

objcoordcat = os.path.join(configdir, objkey + ".cat")

# multiple serial extractions
objkeys = ["obj_" + objname for objname in objnames] # Don't touch my tralala
objdirs = [os.path.join(workdir, o) for o in objkeys]
objkeyflags = ["flag_" + o for o in objkeys]
objcosmicskeys = [o + "_cosmics" for o in objkeys]
objcoordcats = [os.path.join(configdir, o + ".cat") for o in objkeys]


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

renormerrfieldname = renormname + "_err"
renormcommentfieldname = renormname + "_comment"


#---------------------------------------------------------------------------


# F77 MCS config files templates (no need to change anything here)

extract_template_filename = os.path.join(configdir, "template_extract.txt")
psf_template_filename = os.path.join(configdir, "template_psfmofsour8.txt")

old_extract_template_filename = os.path.join(configdir, "template_old_extract.txt")
old_psfm_template_filename = os.path.join(configdir, "template_old_psfmof.txt")
old_lambda_template_filename = os.path.join(configdir, "template_old_lambda.txt")

in_template_filename = os.path.join(configdir, "template_in.txt")
deconv_template_filename = os.path.join(configdir, "template_deconv.txt")

#---------------------------------------------------------------------------


# check for some general dirs

if not os.path.isdir(pipedir):
	print pipedir
	sys.exit("Your pipedir does not exist !")
if not os.path.isdir(configdir):
	print configdir
	sys.exit("Your configdir does not exist !")
if not os.path.isdir(workdir):
	print workdir
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

print "    ### Working in %s ###" % os.path.split(configdir)[-1]

#---------------------------------------------------------------------------


