#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:46:31 2023

@author: fred dux


This file 
 - selects all the images matching our settings.py configuration,
 - extracts the wanted regions fromt hem
 - at the same time, builds a noise map for each region of each image
 - helps the user create masks with ds9
 - applies the created masks to our noise maps (sets noise to 1e8 for masked pixels)

"""

import os
import sys
import h5py
from   pathlib    import Path
import numpy      as     np

sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')
from config import configdir, settings, extracteddir
from modules.variousfct import mterror
from modules import ds9reg


extracteddir = Path(extracteddir)

update = settings['update']
askquestions = settings['askquestions']
refimgname = settings['refimgname']

 

regionsfile = extracteddir / 'regions.h5'
with h5py.File(regionsfile, 'r') as f:
    imgnames = list(f.keys()) # list to get a copy independent of the file

    if not refimgname in imgnames:
        raise mterror(
f"""
Your reference image, f{refimgname} was not extracted. Check what happened, maybe it was rejected
due to a failed procedure at an earlier stage?

In any case, unless something absolutely catastrophic happened, you can still change reference image,
and re-run this script.
""")
    
    # all the extracted objects:
    stamps = f[refimgname]['stamps']
    objects = list(stamps.keys()) # list to get a copy independent of the file
    
    ds9masks = {}
    for i, s in enumerate(objects):
        print('--------------- OBJECT ------------------')
        print(s)
        print('-----------------------------------------')
        
        possiblemaskfilepath = os.path.join(configdir, f"mask_{s}.reg")
        print('mask file path is: ', possiblemaskfilepath)
        if os.path.exists(possiblemaskfilepath):
            stamppixelsx, samptspixelsy = stamps[s].shape
            mask = ds9reg.regions(stamppixelsx, samptspixelsy)
            mask.readds9(possiblemaskfilepath, verbose=False)
            mask.buildmask(verbose=False)
            
            print("You masked %i pixels of star %s." % (np.sum(mask.mask), s))
            ds9masks[s] = mask.mask.T
        else:
            print("No mask file for star %s." % (s))
            

# now, applying the masks:
print('Applying the masks!')
for i, imgname in enumerate(imgnames):

    for i, s in enumerate(objects):
        
        if not s in ds9masks: # If there is no mask for this star
            continue

        with h5py.File(regionsfile, 'r+') as f:
            noisemaps = f[imgname]['noise']
            sig = noisemaps[s][()]
            sig[ds9masks[s]] = 1e8
            noisemaps[s][()] = sig
    

print("- " * 40)

