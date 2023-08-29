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
from   astropy.io import fits

sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')
from config import configdir, settings, extracteddir
from modules.variousfct import mterror, proquest


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




    if not update:
        text = 5*"\n"
        text += "Want me to open DS9 on each object so that you can build a mask?\n"
        text += "Btw for each object the path to where the mask needs to be saved\n"
        text += "will be copied to your clipboard.   So, open DS9? (yes/no) "
        print(text)
        proquest(settings['askquestions'])
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
            call(['ds9', '-cmap', 'heat', '-scale', 'log', starfile])
            # now mask the companion stars in ds9, and save the regions
            # to the file copied in the cilpboard.
            
        tmpdirr.cleanup()


