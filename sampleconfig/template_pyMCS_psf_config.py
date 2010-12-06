#config.py - pyMCS configuration file


###################
### FITS FILE: ####
###################
FILENAME = 'in.fits'
FILE_NB = 1
 
##########################
### General parameters ###
##########################
SHOW = False
CUDA = False

###############################################
#### Sky computation parameters (optional) ####
###############################################
SKY_RANGE = [0.01, 0.97999999999999998]
NBINS = 10
 
##############################
#### Stars finding params ####
##############################
NOBJ = 200
VAL_BND = None
NOWRITE = False
USE_MOMENTS = False
STARS = $starscouplelist$

###############################
#### General parameters    ####
###############################
SKY_BACKGROUND = [0.0]
#SIGMA_SKY = [-0.0034485162840417593]
SIGMA_SKY = [$sigmasky$]
IMG_GAIN = $gain$
NPIX = 64
S_FACT = 2.0
G_RES = 2.0
# Position of the central pixel (NE-SW-O)
CENTER = 'NE'


#################################
#### PSF (Moffat) parameters ####
#################################
MOF_INIT = None
MAX_IT = 0
#[theta, FWHM, ellipticity, beta, Cxi, Cyi, I0i,...]
MOF_PARAMS = [[]]


####################################
#### PSF (Gaussians) parameters ####
####################################
MAX_IT_G = 0
#G_STRAT = '2grids'
#2grid par: itnb, smoothing (fwhmin), inner, idispersion, outer, odispersion
#G_SETTINGS = [ 1000, 0.5, 10, 1, 0, 1] 
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
MAX_IT_N = 200
LAMBDA_NUM = 0.01 # smaller value -> stronger smoothing.
BKG_STEP_RATIO_NUM = 10.0
PSF_RAD = 10.0


##################################
#### Deconvolution parameters ####
##################################
OBJ_POS = (100, 100)
OBJ_SIZE = 64
#BIG PIXELS!!
PSF_SIZE = 64
FFT_DIV = False
D_NB_RUNS = 1
MAX_IT_D = 1000
FORCE_INI = False

##### Background params #####
BKG_INI_CST = 20.0
BKG_STEP_RATIO = 1.0
#BKG_STEP_RATIO = 10000000.0
BKG_START_RATIO = 1.0
LAMBDA = 100000.0

##### Sources params ##### 
NB_SRC = 2
MAX_IRATIO_RANGE = 0.0
MAXPOS_RANGE = 0.0
BOX_SIZE = 10
SRC_RANGE = (0.0, 1000000.0)


################################
#### Deconvolution results #####
IMG_OFFSETS = []
#INI_PAR = [64.170381711993144, 70.803531185702994, 55196.046043601513, 67.655686938141343, 70.344880970991184, 56199.980062790768]
INI_PAR = [64.392966999999999, 71.152160000000066, 55196.046043601513, 67.781036, 70.996346000000003, 56199.980062790768]
#INI_PAR = [65.392966999999999, 72.315216000000007, 115745.046875, 68.781036, 71.996346000000003, 117890.273438]
SRC_PARAMS = [64.392966999999999, 71.315216000000007, 55196.046043601513, 67.781036, 70.996346000000003, 56199.980062790768]






