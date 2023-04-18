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
from   tempfile   import TemporaryDirectory
from   pathlib    import Path
import pyperclip 
from   subprocess import call
import numpy      as     np
from   astropy.io import fits

if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    pass
sys.path.append('..')
from config import configdir, settings, imgdb, extracteddir
from modules.variousfct import proquest, mterror
from modules import ds9reg


stampsize = settings['stampsize']
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
    
    print("You can now open the stamps of your objects with DS9 to build a mask (optional).")
    print("Don't mask cosmics, only, e.g., companion stars!")
    print("Save your region files respectively here:")
    print("(will be copied to your clipboard one by one)")
    
    maskfilepaths = [os.path.join(configdir, f"mask_{obj}.reg") for obj in objects]
    print("\n".join(maskfilepaths))
    
    print("If asked, use physical coordinates and DS9 (or REG) file format.")




    #%%
    if not update:
        text = 5*"\n"
        text += "Want me to open DS9 on each object so that you can build a mask?\n"
        text += "Btw for each object the path to where the mask needs to be saved\n"
        text += "will be copied to your clipboard.   So, open DS9? (yes/no) "
        if input(text) == 'yes':
            tmpdirr = TemporaryDirectory()
            tmpdir = Path(tmpdirr.name)
            
            for obj, maskfile in zip(objects, maskfilepaths):
                data = stamps[obj][()]
                # copy the mask file to the clipboard:
                pyperclip.copy(maskfile)
                print(f'save your region file to \n{maskfile}')
                # store star data in file:
                mfname = Path(maskfile).name
                starfile = tmpdir / (mfname + '.fits')
                fits.writeto(starfile, data)
                # open with ds9
                call(['ds9', starfile])
                # now mask the companion stars in ds9, and save the regions
                # to the file copied in the cilpboard.
                
            tmpdirr.cleanup()



    #%%

    ds9masks = {}
    for i, s in enumerate(objects):
        print('--------------- OBJECT ------------------')
        print(s)
        print('-----------------------------------------')
        
        possiblemaskfilepath = os.path.join(configdir, f"mask_{s}.reg")
        print('mask file path is: ', possiblemaskfilepath)
        if os.path.exists(possiblemaskfilepath):

            mask = ds9reg.regions(stampsize, stampsize) 
            mask.readds9(possiblemaskfilepath, verbose=False)
            mask.buildmask(verbose=False)
            
            print("You masked %i pixels of star %s." % (np.sum(mask.mask), s))
            ds9masks[s] = mask.mask
        else:
            print("No mask file for star %s." % (s))
            
            


# ok, building the masks
# starsarray = h5py.File(psfdir / 'stars.h5', 'r+')
# noisearray = h5py.File(psfdir / 'noisemaps.h5', 'r+')

# now, applying the masks:
print('Applying the masks!')
for i, imgname in enumerate(imgnames):
    #print("%i : %s" % (i+1, imgname))

    for i, s in enumerate(objects):
        
        if not s in ds9masks: # If there is no mask for this star
            continue

        with h5py.File(regionsfile, 'r+') as f:
            noisemaps = f[imgname]['noise']
            sig = noisemaps[s][()]
            sig[ds9masks[s]] = 1e8
            noisemaps[s][()] = sig
    

print("- " * 40)

