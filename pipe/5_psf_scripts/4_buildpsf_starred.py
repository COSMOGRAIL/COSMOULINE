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
import io

from starred.psf.psf import PSF
from starred.psf.loss import Loss
from starred.utils.optimization import Optimizer
from starred.psf.parameters import ParametersPSF
from starred.utils.noise_utils import propagate_noise

# from jax.config import config; config.update("jax_enable_x64", True) #we require double digit precision


if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    pass
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
sys.path.append('..')
from config import settings, psfsfile, starsfile,\
                   cosmicsmasksfile, noisefile, imgdb
from modules.variousfct import mterror
from modules.kirbybase import KirbyBase
from modules.plot_psf import plot_psf
#%%


###############################################################################
###############################################################################
###################### PARAMS
redo = 1

# Parameters
subsampling_factor = 2
n_iter_initial = 20
n_iter = 1000 #epoch for adabelief


lambda_scales = 1
lambda_hf = 1
lambda_positivity = 0.
include_moffat = False
regularize_full_psf = False
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

# We select the images, according to "thisisatest".
# Note that only this first script of the psf construction looks at this :
# the next ones will simply  look for the psfkeyflag in the database !

db = KirbyBase(imgdb)

if settings['thisisatest'] :
    print("This is a test run.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
    print("This is an update.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], returnType='dict')
else :
    images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [True, True], returnType='dict')



# get all image names: (we refered to the data with them in the hdf5 file):
with h5py.File(starsfile, 'r') as f:
    imgnames = list(f.keys())
    
for image in images:
    if not image['imgname'] in imgnames:
        raise mterror(f"{image['imgname']} not found in prepared images!")

#%%
    
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
    # for each image, if huge cosmic, discard image (probably a star trail)
    # for im, no in zip(noisemap, cosmicsmask):
        # print(no.sum())
# 
        # if no.sum() > 40:
            # im[...] = 1e8

    return image, noisemap
#%%  

# get an example:
_image, _ = getData(imgnames[0])

# so we can define a model here (instead of in the loop, avoids recompiling
# every time.)
model = PSF(image_size=_image[0].shape[0], number_of_sources=len(_image), 
            upsampling_factor=subsampling_factor, 
            convolution_method=convolution_method,
            include_moffat=include_moffat)
  


smartguess = lambda im: model.smart_guess(im, fixed_background=True)

# main routine:
def buildPSF(image, noisemap):
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
    
    # normalize by max of data(numerical precision best with scale ~ 1)
    norm = image.max()
    image /= norm
    noisemap /= norm
    
    # Parameter initialization. 
    
    kwargs_init, kwargs_fixed, kwargs_up, kwargs_down = smartguess(image)
    #smartguess doesn't know about cosmics, other stars ...
    kwargs_init['kwargs_gaussian']['x0'] *= 0
    kwargs_init['kwargs_gaussian']['y0'] *= 0
    cc = [0.1, 0.1, 0.1, 0.1]
    kwargs_up['kwargs_gaussian']['x0'] = cc
    kwargs_up['kwargs_gaussian']['y0'] = cc
    kwargs_down['kwargs_gaussian']['x0'] = [-e for e in cc]
    kwargs_down['kwargs_gaussian']['y0'] = [-e for e in cc]
    
    """
    parameters = ParametersPSF(model, 
                               kwargs_init, 
                               kwargs_fixed, 
                               kwargs_up=kwargs_up, 
                               kwargs_down=kwargs_down)
    
    


    loss = Loss(image, model, parameters, noisemap**2, len(image), 
                regularization_terms='l1_starlet', 
                regularization_strength_scales=0, 
                regularization_strength_hf=0) 
        
    # to avoid recompiling at every loop, we update optimizers
    # if we already created them, rather than creating new ones:
    # if not optim:
    optim = Optimizer(loss, 
                      parameters, 
                      # method=method_analytical)
                      method='adabelief')
    # else:
    #     optim._loss = loss
    #     optim._param = parameters 
    #     optim._metrics.param_history = []
    
    # fit the moffat:
    # best_fit, logL_best_fit, extra_fields, runtime = optim.minimize(maxiter=n_iter_initial, 
    #                                                                 restart_from_init=True,
    #                                                                 use_grad=True, 
    #                                                                 use_hessian=False, 
    #                                                                 use_hvp=True)
    
    # 
    
    optimiser_optax_option = {
                                'max_iterations':n_iter, 'min_iterations':None,
                                'init_learning_rate':1e-2, 'schedule_learning_rate':True,
                                # important: restart_from_init True
                                'restart_from_init':True, 'stop_at_loss_increase':False,
                                'progress_bar':True, 'return_param_history':True
                              }           
    
    best_fit, logL_best_fit, extra_fields, runtime = optim.minimize(**optimiser_optax_option)
    
    
    
    kwargs_partial = parameters.args2kwargs(best_fit)
    # now moving on to the background.
    # compute noise level in starlet space, also propagate poisson noise
    W = propagate_noise(model, noisemap, kwargs_partial, 
                        wavelet_type_list=['starlet'], 
                        method='SLIT', num_samples=100,
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
    """
    kwargs_fixed = {
        'kwargs_moffat': {},
        'kwargs_gaussian': {},
        'kwargs_background': {},
    }
    parametersfull = ParametersPSF(model, 
                                   kwargs_init, 
                                   kwargs_fixed, 
                                   kwargs_up, 
                                   kwargs_down)
    
    # W = propagate_noise(model, noisemap, kwargs_init, 
    #                     wavelet_type_list=['starlet'], 
    #                     method='SLIT', num_samples=100,
    #                     seed=1, likelihood_type='chi2', 
    #                     verbose=False, 
    #                     upsampling_factor=subsampling_factor, 
    #                     debug=False)[0]
    
    lossfull = Loss(image, model, parametersfull, 
                    noisemap**2, len(image), 
                    regularization_terms='l1_starlet',
                    regularization_strength_scales=5,#lambda_scales, 
                    regularization_strength_hf=10,
                    regularization_strength_positivity=lambda_positivity, 
                    # W=W, 
                    regularize_full_psf=regularize_full_psf)
    

        
    optimfull = Optimizer(lossfull, parametersfull, method='adabelief')
    
        
    optimiser_optax_option = {
                                'max_iterations':n_iter, 'min_iterations':None,
                                'init_learning_rate':1e-3, 'schedule_learning_rate':True,
                                # important: restart_from_init True
                                'restart_from_init':True, 'stop_at_loss_increase':False,
                                'progress_bar':True, 'return_param_history':True
                              }           
    
    best_fit, logL_best_fit, extra_fields, runtime = optimfull.minimize(**optimiser_optax_option)
    
    # optimfull = Optimizer(lossfull, parametersfull, method=method_analytical)

    
    # best_fit, logL_best_fit, extra_fields, runtime = optimfull.minimize(maxiter=100, 
    #                                                                     restart_from_init=True,
    #                                                                     use_grad=True, 
    #                                                                     use_hessian=False, 
    #                                                                     use_hvp=True)
    
    
    kwargs_final = parametersfull.args2kwargs(best_fit)
    
    ###########################################################################
    # book keeping
    narrowpsf = model.get_narrow_psf(**kwargs_final, norm=True)
    numpsf    = model.get_background(kwargs_final['kwargs_background'])
    moffat    = model.get_moffat(kwargs_final['kwargs_moffat'], norm=True)
    fullmodel = np.array([model.model(i, **kwargs_final) for i in range(image.shape[0])])
    residuals = image - fullmodel
    
    ###########################################################################
    return kwargs_final, narrowpsf, numpsf, moffat, fullmodel, residuals, extra_fields
#%%

# decoy for first loop: we don't have compiled models yet.
# optimtools = {'optim': None, 'optimfull': None}

#%%
from time import time
times = []
# noises = []
# images = []
for i,image in enumerate(images):
    
    imgname = image['imgname']
    t0 = time()
    
    
    # load stamps and noise maps for this image
    data, noisemap = getData(imgname)
    # open the file in which we'll store the result
    with h5py.File(psfsfile, 'r+') as f:
        # check if we need to build again
        if not redo and imgname in f.keys():
            continue
        
        # call the routine defined above 
        kwargs_final, narrowpsf, numpsf, moffat, fullmodel, residuals, extra_fields = buildPSF(data, 
                                                                                               noisemap)
        # time for storage. If key already exists, gotta delete it since
        # h5py does not like overwriting
        for tostore, name in zip([narrowpsf, numpsf, moffat, fullmodel, residuals], 
                                 ['narrow', 'num', 'moffat', 'model', 'residuals']):
            key = f"{imgname}_{name}"
            if key in f.keys():
                del f[key]
            f[key] = tostore
            
    # write plots
    #%%
    if dopsfplots:
        
        try:
            # try because the analytical methods don't have a 'loss_history'
            # field.
            fig = plt.figure(figsize=(2.56, 2.56))
            plt.plot(extra_fields['loss_history'])
            plt.title('loss history')
            plt.tight_layout()
            with io.BytesIO() as buff:
                # write the plot to a buffer, read it with numpy
                fig.savefig(buff, format='raw')
                buff.seek(0)
                plotimg = np.frombuffer(buff.getvalue(), dtype=np.uint8)
                w, h = fig.canvas.get_width_height()
                # white <-> black:
                lossim = 255 - plotimg.reshape((int(h), int(w), -1))[:,:,0].T[:,::-1]
            plt.close()
        except:
            print('no loss history in extra_fields')
            lossim = np.zeros((256,256))
        plot_psf(image, noisemap, lossim)
    # time of iteration
    times.append(time()-t0)

