#    
#    Do the deconvolution of all stars: one point source.
#
import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')
    
    
import h5py
import numpy as np    

from starred.deconvolution.deconvolution import setup_model
from starred.deconvolution.loss import Loss
from starred.utils.optimization import Optimizer
from starred.deconvolution.parameters import ParametersDeconv
    

from config import settings
from modules.deconv_utils import importSettings


askquestions = settings['askquestions']
workdir = settings['workdir']
setnames = settings['setnames']

norm_stars = settings['norm_stars']
subsampling_factor = settings['subsampling_factor']

redo = False

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

    # image positions:
    # just a point source in the center
    xs = np.array([0.])
    ys = np.array([0.])
    
    
    # initial intensity:
    a_est = epochs*[1.5 * np.nanpercentile(data[0], 99.5)]

    model, kwargs_init, kwargs_up, kwargs_down, kwargs_fixed = setup_model(data, sigma_2, s,
                                                                           xs, ys,
                                                                           subsampling_factor,
                                                                           a_est)
    
    # fix the background. (except the mean component)
    kwargs_fixed['kwargs_background']['h'] = kwargs_init['kwargs_background']['h']
    

    parameters = ParametersDeconv(kwargs_init=kwargs_init, 
                                  kwargs_fixed=kwargs_fixed, 
                                  kwargs_up=kwargs_up, 
                                  kwargs_down=kwargs_down)
    

    loss = Loss(data, model, parameters, sigma_2, 
                regularization_terms='l1_starlet', 
                regularization_strength_scales=1, # not needed since no free background...
                regularization_strength_hf=1)# but the starred interface wants us to provdide them anyways
    
    

    optim = Optimizer(loss, parameters, method='adabelief')


    optimiser_optax_option = {
                                'max_iterations':1500, 'min_iterations':None,
                                'init_learning_rate':5e-3, 'schedule_learning_rate':True,
                                'restart_from_init':True, 'stop_at_loss_increase':False,
                                'progress_bar':True, 'return_param_history':True
                            }           

    best_fit, logL_best_fit, extra_fields, runtime = optim.minimize(**optimiser_optax_option)
    
    kwargs_final = parameters.best_fit_values(as_kwargs=True)

    # read the intensities:
    # intensities
    A = [kwargs_final['kwargs_analytic']['a'] * model.scale]
    # write the light curves.
    with h5py.File(decfile, 'r+') as f:
        if 'light_curves' in f.keys():
            del f['light_curves']
        f['light_curves'] = np.array(A)
    
    return kwargs_final, extra_fields


for star in norm_stars:
    # for each star, prepare and stuff
    deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
            decfiles, decskiplists, deckeypsfuseds, ptsrccats = importSettings(star, decnormfieldname="None", decname="noback")

    for decfile, decdir in zip(decfiles, decdirs):
        plotfile = os.path.join(decdir, f"deconv_star_{star}_loss_history.jpg")
        if os.path.exists(plotfile) and not redo:
            print("Well the loss plot is already made, and redo is False.")
            print("skipping.")
            continue
        # one decfile per setname
        kwargs_final, extra_fields = doOneDeconvolution(decfile)
        
        # plot to make sure we're converged.
        plt.figure()
        plt.plot(extra_fields['loss_history'])
        plt.xlabel('iteration number')
        plt.ylabel('loss')
        plt.savefig(plotfile)
    
    
