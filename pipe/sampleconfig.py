import os
import sys
import datetime 
from pathlib import Path
from settingsReader import Settings

# ---------------------------------------------------------------------------
# User settings
# ---------------------------------------------------------------------------

# ----------------------- COMPUTER SETUP -----------------------------
# Choose a computer :
computer = "fred"
# sometimes we call python from inside the scripts.
python = "python"
# here define `sex` (path to your sextractor binary) and `python`.
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
    python = "/scratch/mambaforge/envs/starred-env/bin/python"
# ---------------------------------------------------------------------------

# ----------------------- DIRECTORIES --------- -----------------------------

# The pipeline dir that contains all the scripts (and this "config.py")
# by default, "here"
pipedir = str(Path(__file__).parent)

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

# ------------------------ GENERAL CONFIG ---------------------------------
workdir = settings['workdir']

# The database of the images, fundamental for all scripts :

# This will be an sqlite base.
imgdb = os.path.join(workdir, "database.dat")
# The database is automatically backuped here.
dbbudir = os.path.join(workdir, "backups")    

# Image processing etc is done here:
alidir = os.path.join(workdir, "ali/")      
# We'll store the plots there:
plotdir = os.path.join(workdir, "plots/")

# File with the gaia regions
all_gaia_filename = os.path.join(workdir, 'all_gaia_detections.csv')
filtered_gaia_filename = os.path.join(workdir, 'filtered_gaia_detections.csv')

# ------------------------------ DEFRINGING ---------------------------------
# do you want to defringe your images? (make sure they're dithered ...)
if settings['telescopename'] in ["WFI", "LCO"]:
    defringed = True
else:
    defringed = False


# ------------------------ BEST IMAGE COMBINATION ---------------------------

combibestkey = "combi_" + settings['combibestname']


# ------------------------ COMBINATION BY NIGHT ------------------------------

combinightdirname = 'combinight_' + settings['combinightname']

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

# we expect the fit of the PSF to sometimes fail! This is why we have this file, "psfkicklist" that for a given
# PSF name (usually a list of named stars, e.g., `abc`, per the cosmouline tradition) where the user can add
# the images for which the PSF construction went wrong.
psfkicklist = os.path.join(configdir, psfkey + "_skiplist.txt")
# It's a disallow list used after the psf construction (i.e. that will be used for the deconvolution)
# Note that this can potentially be read by various scripts : this is why
# It is important to KEEP THIS LIST IN YOUR CONFIGDIR, FOR EVERY PSF, AND WITH THIS PRECISE NAME !


# ------------------------ DECONVOLUTION ------------------------------------

# each deconvolution has a name: given by the setname (usually filter of observation), an identifier (decname),
# the object being deconvolved (usually `lens` or a star name, e.g. `a`), a normalization name, and the names of the
# PSFs.
deckeys = [ "dec" \
       + "_" + setname \
       + "_" + settings['decname'] \
       + "_" + settings['decobjname'] \
       + "_" + settings['decnormfieldname'] \
       + "_" + "_".join(settings['decpsfnames'])
         for setname in settings['setnames']]


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
# Don't even think of changing this last one (hard coded in : norm)
maindecdir = os.path.join(workdir, "deconvolutions")
decdirs = [os.path.join(maindecdir, deckey)
               for deckey in deckeys]
decfiles = [os.path.join(decf, 'stamps-noisemaps-psfs.h5') 
                for decf in decdirs]



# -------------------------- NORMALIZATION ----------------------------------

normerrfieldname = settings['normname'] + "_err"
normcommentfieldname = settings['normname'] + "_comment"


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
if not os.path.isdir(maindecdir):
    os.mkdir(maindecdir)
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
