import os
import sys
import datetime 
from pathlib import Path
from settingsReader import Settings

# ---------------------------------------------------------------------------
# User settings :
# ---------------------------------------------------------------------------

# Choose a computer :
computer = "fred"

# The pipeline dir that contains all the scripts (and this "config.py" ) :
pipedir = "/home/fred/Documents/COSMOULINE/pipe/"

# The configuration directory that contains the configuration files :
# ("small-precious-frequently-backuped-disk")
# The scripts do only read, but never write, from here !
configdir = "/scratch/COSMOULINE/WFI_PSJ0030-1525/config/"
#---------------------------------------------------------------------------
# All further settings are made into the configdir.
# You should normally not have to change other lines of this config.py
#---------------------------------------------------------------------------


# to get access to all our modules without installing anything :
sys.path.append(os.path.join(pipedir, "modules"))

# also I want to get rid of the global variables everywhere.
# add the config dir to the path. (Later use a json for the config)
sys.path.append(configdir)
# Read "global parameters" of the lens / deconvolution :
# print(os.path.join(configdir, "settings.py"))


settings = Settings(configdir)


# sometimes we call python from inside the scripts.
python = "python"
# ----------------------- COMPUTER SETUP -----------------------------
if computer=="vivien":
    sex = "/bin/sex"
    #sex = "~/modules/ureka/Ureka/bin/sex"
# ---------------------------------------------------------------------------
if computer=="maltemac":
    sex = "/Applications/sextractor/sex"
    #sex = "/usr/local/bin/sex"
# ---------------------------------------------------------------------------
if computer=="obsds":
    sex = "nice -n 19 /scisoft/bin/sex"
# ---------------------------------------------------------------------------
if computer=="obssr1":
    sex = "nice -n 19 /usr/bin/sex"
# ---------------------------------------------------------------------------
if computer=="rathna":
    sex = "nice -n 19 /scisoft/bin/sex"
# ---------------------------------------------------------------------------
if computer=="topaze":
    sex = "/usr/local/bin/sex"
# ---------------------------------------------------------------------------
if computer=="regor2":
    sex = "nice -n 19 /scisoft/bin/sex"
# ---------------------------------------------------------------------------
if computer=="martin":
    sex = "/sw/bin/sex"
# ---------------------------------------------------------------------------
if computer=="fred":
    sex = "/usr/bin/sex"
    python = "/home/fred/anaconda3/bin/python"
+   python = "/home/fred/anaconda3/envs/starred-env/bin/python"


# Path to compiled programs :

mcsf77dir = os.path.join(pipedir, "progs", "MCSf77")

if computer == "vivien":
    mcsf77dir = '/home/vivien/modules/MCSf77'


prefix = ""
extractexe = prefix + os.path.join(mcsf77dir, "extract.exe")
psfexe = prefix + os.path.join(mcsf77dir, "psf.exe")
deconvexe = prefix + os.path.join(mcsf77dir, "deconv.exe")
if settings['silencemcs'] == True:
    psfexe = prefix + os.path.join(mcsf77dir, "psf_silence.exe")
    deconvexe = prefix + os.path.join(mcsf77dir, "deconv_silence.exe")


# ------------------------ GENERAL CONFIG ---------------------------------
workdir = settings['workdir']

# The database of the images, fundamental for all scripts :

# This will be an sqlite base.
imgdb = os.path.join(workdir, "database.dat")
# The database is automatically backuped here.
dbbudir = os.path.join(workdir, "backups")    

# Alignment etc is done here
alidir = os.path.join(workdir, "ali/")      
# Some plots will go here (not used anymore)  
plotdir = os.path.join(workdir, "plots/")    

# Image lists (line format : imgname comment 
# (you can leave blank lines and use "#" to comment a line !)) :
imgkicklist = os.path.join(configdir, "kicklist.txt")    
# Images that get "gogogo" set to False by the extrascript "kickimg.py",
# as they simply cannot be used (too faint, cosmic on lens, etc)
# No other script uses that list.


testlist = os.path.join(configdir, "testlist.txt")            
# This is an "allow list" for test runs (e.g. psf construction, ...).
# Write images + comments on this list, and use the extrascri   pt "set_testlist.py"
# to set the "testlist" and "testcomment" flags in the database.
# This list is also handy if you want to rebuild some handpicked psfs after 
# a change of some parameters for instance !


# File with the coordinates of the regions
regionscat = os.path.join(configdir, 'regions.cat')

# ------------------------------ DEFRINGING ---------------------------------
# do you want to work on defringed images (if they exists ?)
if settings['telescopename'] in ["WFI", "LCO"]:
    defringed = True
else :
    defringed = False


# ------------------------ BEST IMAGE COMBINATION ---------------------------

combibestkey = "combi_" + settings['combibestname']


# ------------------------ COMBINATION BY NIGHT ------------------------------

combinightdirname = 'combinight_'  + settings['combinightname']

combinightdirpath = os.path.join(workdir, combinightdirname)


# ------------------------ PSF CONSTRUCTION ---------------------------------

psfkey = "psf_" + settings['psfname']     # Don't touch (all this is hard-coded in the first dec prepfiles script !)
psfdir = os.path.join(workdir, psfkey)    # Don't touch
psfkeyflag = "flag_" + psfkey             # Don't touch
psfcosmicskey = psfkey + "_cosmics"       # Don't touch

# files
psfdirc = Path(psfdir)
starsfile = psfdirc / 'stars.h5'
noisefile = psfdirc / 'noisemaps.h5'
cosmicsmasksfile = psfdirc / 'cosmics_masks.h5'
psfsfile = psfdirc / 'psfs.h5'
psfsplotsdir = psfdirc / 'plots'
if not psfsplotsdir.exists():
    psfsplotsdir.mkdir(parents=True, exist_ok=True)
extracteddir = Path(workdir) / 'extracteddir'
if not extracteddir.exists():
    extracteddir.mkdir(parents=True, exist_ok=True)


cosmicslabelfile = extracteddir / 'cosmics_labels.json'


# file with psf star coordinates (lineformat : "somename x y")
psfstarcat = os.path.join(configdir, psfkey + ".cat")
psfkicklist = os.path.join(configdir, psfkey + "_skiplist.txt")
# Its a black list *after* the psf construction (i.e. that will be used for the deconvolution)
# Note that this can potentially be read by various scripts : this is why
# It is important to KEEP THIS LIST IN YOUR CONFIGDIR, FOR EVERY PSF, AND WITH THIS PRECISE NAME !


# ------------------------ OBJECT EXTRACTION --------------------------------
# single extraction

objkey = "obj_" + settings['objname']   # Don't touch, it would screw more than you can think of !
objdir = os.path.join(workdir, objkey)  # Don't touch, same...
objkeyflag = "flag_" + objkey           # Don't touch
objcosmicskey = objkey + "_cosmics"     # Don't touch

objcoordcat = os.path.join(configdir, objkey + ".cat")

# multiple serial extractions
objkeys = ["obj_" + objname for objname in settings['objnames']]
objdirs = [os.path.join(workdir, o) for o in objkeys]
objkeyflags = ["flag_" + o for o in objkeys]
objcosmicskeys = [o + "_cosmics" for o in objkeys]
objcoordcats = [os.path.join(configdir, o + ".cat") for o in objkeys]


# ------------------------ DECONVOLUTION ------------------------------------

# I like to do many deconvolutions... we could choose an explicit deckey like :
deckeys = [ "dec" \
       + "_" + setname \
       + "_" + settings['decname'] \
       + "_" + settings['decobjname'] \
       + "_" + settings['decnormfieldname'] \
       + "_" + "_".join(settings['decpsfnames'])
         for setname in settings['setnames']]


# where the initial position and intensities are written
ptsrccats = [os.path.join(configdir, deckey + "_ptsrc.cat") 
                 for deckey in deckeys]
# put here images that you do not want to include 
# in this particular deconvolution.
decskiplists = [os.path.join(configdir, deckey + "_skiplist.txt")
                 for deckey in deckeys]
# the name of the field that contains 001, 002 etc
deckeyfilenums = ["decfilenum_" + deckey
                    for deckey in deckeys]
# the name of the field to contain the used psfname for "this particular image"
deckeypsfuseds = ["decpsf_" + deckey
                    for deckey in deckeys]
# the name of the field to contain the normalization 
# coeff that was actually used
deckeynormuseds = ["decnorm_" + deckey
                    for deckey in deckeys]
# Don't even think of changing this last one (hard coded in : renorm)
decdirs  = [os.path.join(workdir, deckey) 
                for deckey in deckeys]
decfiles = [os.path.join(decf, 'stamps-noisemaps-psfs.h5') 
                for decf in decdirs]



# ------------------------ RENORMALIZATION ----------------------------------

renormerrfieldname = settings['renormname'] + "_err"
renormcommentfieldname = settings['renormname'] + "_comment"


# ---------------------------------------------------------------------------


# F77 MCS config files templates (no need to change anything here)

extract_template_filename = os.path.join(configdir, "template_extract.txt")
psf_template_filename = os.path.join(configdir, "template_psfmofsour8.txt")

old_extract_template_filename = os.path.join(configdir, "template_old_extract.txt")
old_psfm_template_filename = os.path.join(configdir, "template_old_psfmof.txt")
old_lambda_template_filename = os.path.join(configdir, "template_old_lambda.txt")

in_template_filename = os.path.join(configdir, "template_in.txt")
deconv_template_filename = os.path.join(configdir, "template_deconv.txt")

# ---------------------------------------------------------------------------


# check for some general dirs

if not os.path.isdir(pipedir):
    print(pipedir)
    sys.exit("Your pipedir does not exist !")
if not os.path.isdir(configdir):
    print(configdir)
    sys.exit("Your configdir does not exist !")
if not os.path.isdir(workdir):
    print(workdir)
    sys.exit("Your workdir does not exist !")


if not os.path.isdir(alidir):
    os.mkdir(alidir)
if not os.path.isdir(plotdir):
    os.mkdir(plotdir)
if not os.path.isdir(dbbudir):
    os.mkdir(dbbudir)
# ---------------------------------------------------------------------------

############ Building the filenames ##############
lensName = settings['lensName']
now = datetime.datetime.now()
datestr = now.strftime("%Y-%m-%d")
filename = f"{datestr}_{lensName}"

readmefilepath = os.path.join(configdir, filename + "_readme.txt")
pklfilepath = os.path.join(configdir, filename + "_db.pkl")
pklgenericfilepath = os.path.join(configdir, f"{lensName}_db.pkl")
dbcopyfilepath = os.path.join(configdir, filename + "_db.dat")

# ---------------------------------------------------------------------------


print(f"### Config dir: {configdir} ###")

# ---------------------------------------------------------------------------


