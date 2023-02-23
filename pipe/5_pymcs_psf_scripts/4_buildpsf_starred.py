#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 22:14:26 2023

@author: fred

Here we use STARRED to build our PSF. 
"""

import sys
import os
import numpy as np
import h5py

from starred.psf.psf import PSF
from starred.psf.loss import Loss
from starred.utils.optimization import Optimizer
from starred.psf.parameters import ParametersPSF
from starred.plots import plot_function as pltf
from starred.utils.noise_utils import propagate_noise

from jax.config import config; config.update("jax_enable_x64", True) #we require double digit precision


if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    pass
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
sys.path.append('..')
from config import settings, psfdir, psfsplotsdir, psfsfile, starsfile,\
                   cosmicsmasksfile, noisefile
from modules.variousfct import proquest, notify
from modules.kirbybase import KirbyBase



###############################################################################
###############################################################################
###################### PARAMS
redo = 1

# Parameters
subsampling_factor = 2
n_iter_initial = 30
n_iter = 1000 #epoch for adabelief


lambda_scales = 1.
lambda_hf = 1.
lambda_positivity = 0. 
include_moffat = True
regularize_full_psf = True
convolution_method = 'fft'
method_analytical = 'trust-constr'

###############################################################################
###############################################################################

# params from settings.py
dopsfplots = settings['dopsfplots']




if dopsfplots:
    import matplotlib.pyplot as plt
    plt.switch_backend('agg')

# if h5 file storing psf has never been created,
if not psfsfile.exists():
    # just create it.
    with h5py.File(psfsfile, 'w') as f:
        pass




# get all image names: (we refered to the data with them in the hdf5 file):
with h5py.File(starsfile, 'r') as f:
    imgnames = list(f.keys())
    
    
# a utility to load the data of one image:
def getData(imgname):
    with h5py.File(starsfile, 'r') as f:
        image = np.array(f[imgname])
    with h5py.File(cosmicsmasksfile, 'r') as f:
        cosmicsmask = np.array(f[imgname+'_mask'])
    with h5py.File(noisefile, 'r') as f:
        noisemap = np.array(f[imgname])
    
    # mask cosmics here.
    noisemap[cosmicsmask] = 1e8

    return image, noisemap
  

# get an example:
_image, _ = getData(imgnames[0])

# so we can define a model here (instead of in the loop, avoids recompiling
# every time.)
model = PSF(image_size=_image[0].shape[0], number_of_sources=len(_image), 
            upsampling_factor=subsampling_factor, 
            convolution_method=convolution_method,
            include_moffat=include_moffat)
  

# main routine:
def buildPSF(image, noisemap, loss=None, optim=None, lossfull=None, optimfull=None):
    """
    

    Parameters
    ----------
    image : array, shape (imageno, nx, ny)
        array containing the data
    noisemap : array, shape (imageno, nx, ny)
        array containing the noisemaps.
    loss : starred.psf.loss, optional
        This 
    optim : TYPE, optional
        DESCRIPTION. The default is None.
    lossfull : TYPE, optional
        DESCRIPTION. The default is None.
    optimfull : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    kwargs_final : TYPE
        DESCRIPTION.
    narrowpsf : TYPE
        DESCRIPTION.
    numpsf : TYPE
        DESCRIPTION.
    moffat : TYPE
        DESCRIPTION.
    optimtools : TYPE
        DESCRIPTION.

    """
    
    # Parameter initialization. 
    kwargs_init, kwargs_fixed, kwargs_up, kwargs_down = model.smart_guess(image, 
                                                                          fixed_background=1)
    
    parameters = ParametersPSF(model, 
                               kwargs_init, 
                               kwargs_fixed, 
                               kwargs_up=kwargs_up, 
                               kwargs_down=kwargs_down)
    
    
    # to avoid recompiling at every loop, we update the loss and optimizers
    # if we already created them, rather than creating new ones:
    if loss:
        loss.update_dataset(image, noisemap**2, newW=None, newparam_class=parameters)
    else:
        loss = Loss(image, model, parameters, noisemap**2, len(image), 
                    regularization_terms='l1_starlet', 
                    regularization_strength_scales=0, 
                    regularization_strength_hf=0) 
    if not optim:
        optim = Optimizer(loss, 
                          parameters, 
                          method=method_analytical)
    else:
        optim._loss = loss
        optim._param = parameters 
    
    
    # fit the moffat:
    best_fit, logL_best_fit, extra_fields, runtime = optim.minimize(maxiter=n_iter_initial, 
                                                                    restart_from_init=True,
                                                                    use_grad=True, 
                                                                    use_hessian=False, 
                                                                    use_hvp=True)
    
    kwargs_partial = parameters.args2kwargs(best_fit)
    
    
    # now moving on to the background.
    # compute noise level in starlet space, also propagate poisson noise
    W = propagate_noise(model, noisemap, kwargs_partial, 
                        wavelet_type_list=['starlet'], 
                        method='SLIT', num_samples=5000,
                        seed=1, likelihood_type='chi2', 
                        verbose=False, 
                        upsampling_factor=subsampling_factor, 
                        debug=False)[0]
    
    # Release backgound, fix the moffat
    kwargs_fixed = {
        'kwargs_moffat': {'fwhm': kwargs_partial['kwargs_moffat']['fwhm'], 
                          'beta': kwargs_partial['kwargs_moffat']['beta'], 
                          'C': kwargs_partial['kwargs_moffat']['C']},
        'kwargs_gaussian': {},
        'kwargs_background': {},
    }
    
    parametersfull = ParametersPSF(model, 
                                   kwargs_partial, 
                                   kwargs_fixed, 
                                   kwargs_up, 
                                   kwargs_down)
    
    
    if not lossfull:
        lossfull = Loss(image, model, parametersfull, 
                        noisemap**2, len(image), 
                        regularization_terms='l1_starlet',
                        regularization_strength_scales=lambda_scales, 
                        regularization_strength_hf=lambda_hf,
                        regularization_strength_positivity=lambda_positivity, 
                        W=W, 
                        regularize_full_psf=regularize_full_psf)
    else:
        lossfull.update_dataset(image, noisemap**2, 
                                newW=W, 
                                newparam_class=parametersfull)
    
    if not optimfull:
        optimfull = Optimizer(lossfull, parametersfull)
    else:
        optimfull._loss = lossfull
        optimfull._param = parametersfull 
        
        
    best_fit, logL_best_fit, extra_fields, runtime = optimfull.optax(
                  algorithm='adabelief', max_iterations=n_iter, min_iterations=None,
                  init_learning_rate=2e-2, schedule_learning_rate=True,
                  restart_from_init=False, stop_at_loss_increase=False,
                  progress_bar=True, return_param_history=True
                  )
    
    kwargs_final = parametersfull.args2kwargs(best_fit)
    
    if dopsfplots:
        for n_psf in range(image.shape[0]):
            fig = pltf.single_PSF_plot(model, image, noisemap**2, kwargs_final, 
                                       n_psf=n_psf, units='e-')
            fig.savefig(psfsplotsdir / ( imgname + f'_{n_psf}.png' ) )
            plt.close()
    narrowpsf = model.get_narrow_psf(**kwargs_final, norm=True)
    numpsf    = model.get_background(kwargs_final['kwargs_background'])
    moffat    = model.get_moffat(kwargs_final['kwargs_moffat'], norm=True)
    
    optimtools = {'loss': loss, 'lossfull': lossfull,
                  'optim': optim, 'optimfull': optimfull}
    
    #######################################################################
    return kwargs_final, narrowpsf, numpsf, moffat, optimtools


# decoy for first loop
optimtools = {'loss': None, 'lossfull': None,
              'optim': None, 'optimfull': None}


for imgname in imgnames:
    # load stamps and noise maps for this image
    image, noisemap = getData(imgname)
    
    # open the file in which we'll store the result
    with h5py.File(psfsfile, 'r+') as f:
        # check if we need to build again
        if not redo and imgname in f.keys():
            continue
        
        # call the routine defined above 
        kwargs_final, narrowpsf, numpsf, moffat, optimtools = buildPSF(image, 
                                                                       noisemap, 
                                                                       **optimtools)
        # time for storage. If key already exists, gotta delete it since
        # h5py does not like overwriting
        if imgname in f.keys():
            del f[imgname]
        f[imgname] = narrowpsf


