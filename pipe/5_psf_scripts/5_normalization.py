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
import progressbar


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


refimgname = settings['refimgname']

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

renorm_coeff_name = 'renorm_' + settings['psfname']
renormerrfieldname = renorm_coeff_name + '_err'

with h5py.File(psfsfile, 'r') as f:

    fullrefmodel = f[f"{refimgname}_model"]
    refintensities = np.sum(fullrefmodel, axis=(1,2))
    for image in images:
        imgname = image['imgname']
        fullmodel = f[f"{imgname}_model"]
        coeffs = np.sum(fullmodel, axis=(1,2)) / refintensities
        image[renorm_coeff_name] = np.mean(coeffs)
        image[renormerrfieldname] = np.std(coeffs)

# add all this to the database


# but first get rid of existing
if renorm_coeff_name in db.getFieldNames(imgdb):
    print("The field", renorm_coeff_name, "already exists in the database.")
    print("I will erase it.")
    db.dropFields(imgdb, [renorm_coeff_name])
    if renormerrfieldname in db.getFieldNames(imgdb):
        db.dropFields(imgdb, [renormerrfieldname])
# add again
db.addFields(imgdb, [f'{renorm_coeff_name}:float', 
                     f'{renormerrfieldname}:float'])

widgets = [progressbar.Bar('>'), ' ',
           progressbar.ETA(), ' ',
           progressbar.ReverseBar('<')]
pbar = progressbar.ProgressBar(widgets=widgets, 
                               maxval=len(images)+2).start()

for i, image in enumerate(images):
    pbar.update(i)
    db.update(imgdb, ['recno'], 
                     [image['recno']], 
                     {
                         renorm_coeff_name: float(image[renorm_coeff_name]), 
                         renormerrfieldname: float(image[renormerrfieldname])
                     })