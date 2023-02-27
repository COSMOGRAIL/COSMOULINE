#    
#    Do the deconvolution
#    STARRED update: we will use a jupyter notebook to do this step, as it
#    requires a lot of user input. 
#
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
    
    
import h5py
import numpy as np    

from starred.deconvolution.deconvolution import Deconv
from starred.deconvolution.loss import Loss
from starred.utils.optimization import Optimizer
from starred.deconvolution.parameters import ParametersDeconv
from starred.utils.noise_utils import propagate_noise
    

from config import imgdb, settings, computer, deconvexe
from modules.variousfct import proquest, notify, nicetimediff
from modules.kirbybase import KirbyBase
from settings_manager import importSettings


askquestions = settings['askquestions']
workdir = settings['workdir']
setnames = settings['setnames']








# import the right deconvolution identifiers:
scenario = "normal"
if len(sys.argv)==2:
    scenario = "allstars"
    decobjname = sys.argv[1]
if settings['update']:
    scenario = "update"
    askquestions = False
    
deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decfiles, decskiplists, deckeypsfuseds, ptsrccats = importSettings(scenario)
           
           
def doOneDeconvolution(decfile):
    
    # load data
    with h5py.File(decfile, 'r') as f:
        sigma_2 = np.array(f['noisemaps'])**2
        s = np.array(f['psfs']) # narrow psf
        data = np.array(f['stamps'])
        
    im_size = data[0].shape[0]
    im_size_up = s[0].shape[0]
    subsampling_factor = im_size_up // im_size 
    
    epochs = data.shape[0]
    
    
    # Parameter initialization

    # image positions:
    # just a point source in the center
    xs = np.array([0.])
    ys = np.array([0.])
    
    # number of point sources .... 1
    M = xs.size 
    
    initial_c_x = xs * subsampling_factor 
    initial_c_y = ys * subsampling_factor 
    # initial intensity:
    a_est = np.percentile(data[0], 99.5)
    initial_a = 1.65*np.array(epochs*[a_est])
    # provide a normalization for the image, makes things numerically more tractable:
    scale = data.max()
    initial_a /= scale
    # we will also provide the Deconvolution class with this scale at the end of this cell.
    
    # initial background:
    initial_h = np.zeros((im_size_up**2))
    
    
    
    # dictionary containing the parameters of deconvolution.
    # (The translations dx, dy are set to zero for the first epoch.
    # Thus we only initialize (epochs-1) of them.)
    kwargs_init = {
        'kwargs_analytic': {
                            'c_x': initial_c_x,
                            'c_y': initial_c_y,
                            'dx' : np.ravel([0. for _ in range(epochs-1)]),
                            'dy' : np.ravel([0. for _ in range(epochs-1)]),
                            'a'  : initial_a},
        'kwargs_background': {'h': initial_h,
                              'mean': np.ravel([0. for _ in range(epochs)])},
    }
    # same as above, providing fixed parameters:
    kwargs_fixed = {
        'kwargs_analytic': {
            'c_x': initial_c_x, 
            'c_y': initial_c_y, 
            # 'a'  : initial_a
        },
        'kwargs_background': {'h': initial_h},
    }
    
    
    # boundaries.
    kwargs_up = {
        'kwargs_analytic': {'c_x': list(initial_c_x+3),
                            'c_y': list(initial_c_y+3),
                            'dx' : [5 for _ in range(epochs-1)],
                            'dy' : [5 for _ in range(epochs-1)],
                             'a': list([np.inf for i in range(M*epochs)]) 
                           },
        'kwargs_background': {'h': list([np.inf for i in range(0, im_size_up**2)]),
                              'mean': [np.inf for _ in range(epochs)]
                               },
    }
    
    kwargs_down = {
        'kwargs_analytic': {'c_x': list(initial_c_x-3),
                            'c_y': list(initial_c_y-3),
                            'dx' : [-5 for _ in range(epochs-1)],
                            'dy' : [-5 for _ in range(epochs-1)],
                             'a': list([0 for i in range(M*epochs)]) },
        'kwargs_background': {'h': list([-np.inf for i in range(0, im_size_up**2)]),
                              'mean': [-np.inf for _ in range(epochs)]
                               },
            }
    
    # Initializing the model
    model = Deconv(image_size=im_size, 
                   number_of_sources=M, 
                   scale=scale, 
                   upsampling_factor=subsampling_factor, 
                   epochs=epochs, 
                   psf=s, 
                   convolution_method='fft')
    
    
    
    # compute noise level in starlet space
    W = propagate_noise(model, np.sqrt(sigma_2), kwargs_init, wavelet_type_list=['starlet'], 
                        method='MC', num_samples=200, seed=1, likelihood_type='chi2', 
                        verbose=False, upsampling_factor=subsampling_factor, debug=False)[0]
    
    
    # allow everything to be optimized at once.
    kwargs_fixed = {
        'kwargs_analytic': {},
        'kwargs_background': {},
    }
    
    parameters = ParametersDeconv(model, 
                                  kwargs_init=kwargs_init, 
                                  kwargs_fixed=kwargs_fixed, 
                                  kwargs_up=kwargs_up, 
                                  kwargs_down=kwargs_down)
    
    loss = Loss(data, model, parameters, sigma_2, 
                regularization_terms='l1_starlet', 
                regularization_strength_scales=1, 
                regularization_strength_hf=1, W=W) 
    
    
    optim = Optimizer(loss, parameters)
    best_fit, logL_best_fit, extra_fields, runtime = optim.optax(
                  algorithm='adabelief', max_iterations=10000, min_iterations=None,
                  init_learning_rate=0.001, schedule_learning_rate=False,
                  restart_from_init=True, stop_at_loss_increase=True,
                  progress_bar=True, return_param_history=True
                  )
    
    kwargs_final = parameters.best_fit_values(as_kwargs=True)
    
    return kwargs_final



    
    


for decfile in decfiles:
    pass


