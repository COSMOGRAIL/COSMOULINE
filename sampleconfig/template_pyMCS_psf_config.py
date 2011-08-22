#config.py - pyMCS configuration file

###################
### FITS FILE: ####
###################
#Name of the image (use * for multiple images):
FILENAME = 'in.fits'
#number of files (will disappear soon):
FILE_NB = 1
 
##########################
### General parameters ###
##########################
#True for showing the results on the screen (DS9, matplotlib):
SHOW = False
#True if you want to use CUDA (if available):
CUDA = False

###############################################
#### Sky computation parameters (optional) ####
###############################################
#Portion of the pixels to be taken into account when computing the sky value (quantile):
#e.g: [0.1, 0.9]
SKY_RANGE = [0.01, 0.99]
#Number of bins used for the gaussian fit: 
NBINS = 30
 
##############################
##### Star search params #####
##############################
INTERACTIVE = False
#nb of candidate to acquire:
NOBJ = 100
#range of the stars' peak values (e.g.: '(0,10000)'):  
VAL_BND = None
#Set the following to True if you only want to see the results without saving them:
NOWRITE = False
#Set to true if you want to evaluate the candidate by using the moments instead of a gaussian fit:
USE_MOMENTS = False
#position of the stars used for the PSF:
STARS = $starscouplelist$
#number of pixels to extract for the PSF:
NPIX = 64

###############################
#### General parameters ####
###############################
#Sky value:
SKY_BACKGROUND = [0.]
#Sigma in the image:
SIGMA_SKY = [$sigmasky$]
#Image gain:
IMG_GAIN = $gain$
#Sampling factor:
S_FACT = 2.0
#Final resolution of the deconvolved image (FWHM):
G_RES = 2.0
# Position of the central pixel (NE-SW-O) ##unused##
CENTER = 'SW'


#################################
#### PSF (Moffat) parameters ####
#################################
#Initial parameters of the moffat profile (default: None):
MOF_INIT = None
#Maximum number of iteration during the fit:
MAX_IT = 0
#Resulting Moffat parameters:
#[theta, FWHM, ellipticity, beta, Cxi, Cyi, I0i,...]
MOF_PARAMS = [[]]


####################################
#### PSF (Gaussians) parameters ####
####################################
MAX_IT_G = 0
#2grid par: itnb, smoothing (fwhmin), inner, idispersion, outer, odispersion
#[itnb, gnb, gsize, fwhmin]
G_SETTINGS = [0, 30, 0, 2.0]
G_STRAT = 'mixed'
FIT_RAD = None
NB_RUNS = 1

#resulting parameters:
G_PARAMS = [[]]
G_POS = [[]]



##############################
#### PSF (num) parameters ####
##############################
# Number of iterations:
MAX_IT_N = 100
# the higher the smoother 
LAMBDA_NUM = 1.0E3
#Wavelet threshold used during the regularization (default: None):
WL_THRESHOLD_NUM = None
WL_THRESHOLD_DEC = None
#don't touch... will disapear soon
BKG_STEP_RATIO_NUM = 1.0
#radius of the relevant part of the stars:
PSF_RAD = 100.0
#min step during background fit (default: None)
MIN_STEP_NUM = 0.00005
#max step during background fit (default: None)
MAX_STEP_NUM = 0.005
#size of the final PSF (using zero-pdding):
#BIG PIXELS!!
PSF_SIZE = 64

##################################
#### Deconvolution parameters ####
##################################
#Position of the object to deconvolve
OBJ_POS = (64, 64)
#size of the image to deconvolve
OBJ_SIZE = 64
#size of the PSF (same as OBJ_SIZE, will disapear soon):
#BIG PIXELS!!
PSF_SIZE = 64
#True if you want to use FFT division to estimate the initial parameters of the deconvolution:
FFT_DIV = False
#Number of times the whole deconvolution should be done:
D_NB_RUNS = 1
#Number of iteration for each deconvolution:
MAX_IT_D = 300
#True if you want to evaluate the initial parameters at each convolution:
FORCE_INI = False

##### Background params #####
#Initial background value (override the initial parameters):
BKG_INI_CST = 0.0
#don't touch... will disapear soon
BKG_STEP_RATIO = 1.0
#don't touch... will disapear soon
BKG_START_RATIO = 1.0
#smoothing of the background (the lower the smoother):
LAMBDA = 100000.0
#min step during background fit (default: None)
MIN_STEP_D = 5e-06
#max step during background fit (default: None)
MAX_STEP_D = 0.0005

##### Sources params ##### 
#number of sources in the image:
NB_SRC = 0
#allowed range for the intensity of the sources (ratio, not percentage):
MAX_IRATIO_RANGE = 0.2
#allowed range for the position (in pixels):
MAXPOS_RANGE = 1.0
#minimum padding between two sources (in pixels):
BOX_SIZE = 10
#range of the sources' peak values (e.g.: '(0,10000)'):  
SRC_RANGE = (0.0, 1000000.0)


################################
#### Deconvolution results #####
################################
#offests between the images: 
IMG_OFFSETS = []
#initial parameters of the sources:
INI_PAR = []
#final parameters of the sources:
SRC_PARAMS = []






