

section = {
'config': 
"""Here are listed all the parameters of the choosen configuration """
"""file needed during the entire deconvolution process. You may """
"""either change them now or during each phase.""",
'prepare': 
"""This section allows you to estimate some parameters that you """
"""may not have easily at hand.""",
'sky': 
"""This little program will look for the sky background of the image by """
"""fitting a gaussian on the pixel distribution. The center of the """
"""gaussian will give the sky value and the FWHM will define the standard """
"""deviation.""",
'ssearch':
"""The next program will try to find some good looking stars in the image, """
"""by classifying the object according to their ellipticity, rotation and """
"""FWHM.""",
'ssel':
"""Select the candidates which seem the most appropriate to construct the PSF""",
'moffit':
"""The first part of the PSF is built by fitting a moffat to the stars.""",
'gausfit':
"""We will now try to reduce the residuals from the moffat fit by by adding """
"""gaussians to the PSF at the most relevant places."""}


entry = {   
'SKY_RANGE': """Proportion of the pixel taken for the sky computation. """
"""It is expressed in quantiles. Default is (0.01,0.99)""",
'NBINS': """Number of bins of the histogram to which the gaussian """
"""will be fitted. If a bad looking shape appears, try setting it to a """
"""smaller value (e.g 40). Default: None""",
'SKY_BACKGROUND': """Value of the sky in the image. It is supposed to be """
"""constant on all the data""",
'SIGMA_SKY': """Standard deviation of the sky""",
'IMG_GAIN': """Gain of the CCD (electron to ADU)""",
'NOBJ': """Number of objects used to find the stars. Default: 100""",
'VAL_BND': """Only object with a maximal value inside these bounds """
"""will be taken into account (default: None)""",
'candidates': """Positions of the resulting candidates:""",
'spos': """Position of the stars""",
'NPIX': """Size of the extracted images""",
'S_FACT': """Sampling factor (ratio to the small pixels used for the PSF""",
'G_RES': """Gaussian resolution (FWHM of the convolution gaussian):""",
'CENTER': """Define on which pixel (relative to the central pixel) the center"""
""" of the PSF should be. It may be NE (default), SW or O (origin).
\nIMPORTANT: for compatibility with the fortran implementation, you need a PSF"""
"""centered NE. However, the python convolution needs a SW centered PSF.""",
'MOF_INIT': """Initial parameters for the moffat fit (default: None)""",
'MAX_IT': """Maximum number of function evaluation during the minimization""",
'MOF_PARAMS': """Final moffat parameters""",
'G_STRAT': """Strategy used for placing the gaussians on the good spots. The most """
"""useful are 'weighted' (default) and 'mixed'. The first construct a median image """
"""of the residuals and weighted according to their noisemap and place the gaussians """
"""on it while the second places them directly on the residuals.""",
'G_SETTINGS': """Settings used by the strategy. They are in the form: """
"""[it_nb, gaus_nb, gaus_size, fwhm_min] where gaus_size is the spacing """
"""between each gaussian. Default: [300, 6, 0, 2.]""",
'NB_RUNS': """There is a possibility to make successive runs of the gaussian fit:""",
'G_PARAMS': """Gaussians parameters [intesity, FWHM]""",
'G_POS': """Gaussians positions"""}


