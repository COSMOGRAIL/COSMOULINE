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
from config import configdir, settings, imgdb, dbbudir,\
                   alidir, extracteddir, regionscat
from modules.variousfct import proquest, backupfile, mterror
from modules import star
from modules import ds9reg
from modules.kirbybase import KirbyBase


stampsize = settings['stampsize']
alidir = Path(alidir)
extracteddir = Path(extracteddir)

update = settings['update']
askquestions = settings['askquestions']
refimgname = settings['refimgname']

db = KirbyBase(imgdb)

 
regions = star.readmancat(regionscat)


# now to calculate the noise maps, we need an estimation of the background noise!
# so the "empty" region must be in regions:
if not 'empty' in [s.name for s in regions]:
    raise mterror(
    """
    I do not have an empty region to calculate 
    the standard deviation of the background from!
                        
    Please select an empty region in the `0_pick_regions.py` script
    and re-run this one.
    """
    )

# split the empty region and other objects:
empty = [reg for reg in regions if reg.name == 'empty'][0]
objects = [reg for reg in regions if not reg.name == 'empty']


# We select the images, according to "thisisatest".
# Note that only this first script of the psf construction looks at this :
# the next ones will simply look for the psfkeyflag in the database !
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


print(f"I will treat {len(images)} images.")
proquest(askquestions)


# where we'll save our stamps
regionsfile = extracteddir / 'regions.h5'
# start from scratch ...
if regionsfile.exists():
    # delete if exists.
    regionsfile.unlink()


for i,image in enumerate(images):
    print(40*"- ")
    print("%i / %i : %s" % (i+1, len(images), image['imgname']), end= ' ')
    
    alifile = alidir / f"{image['imgname']}_ali.fits"
    
    # aligned images are in e-
    try:
       alidata = fits.getdata(alifile)
    except:
       db.update(imgdb, ['recno'], [image['recno']], [False], ['gogogo'])
       continue
    
    # noise map
    # first need to read the noise level of the image. 
    h = stampsize // 2
    x, y = int(empty.x), int(empty.y)
    emptyarray = alidata[y-h:y+h, x-h:x+h]
    stddev = np.nanstd(emptyarray)
    print(f'(stddev of background: {stddev:.01f})')
    with h5py.File(regionsfile, 'a') as regf:
        # organize hdf5 file
        imset = regf.create_group(image['imgname'])
        stampset = imset.create_group('stamps')
        noiseset = imset.create_group('noise')
        # useful when masking cosmics.
        _ = imset.create_group('cosmicsmasks')

        # extract the regions
        for obj in objects:
            x, y = int(obj.x), int(obj.y)
            reg = alidata[y-h:y+h, x-h:x+h]
            # noise map given that the data is in electrons ...
            nmap = stddev + np.sqrt(np.abs(reg))
            # remove zeros if there are any ...
            nmap[nmap < 1e-7] = 1e-7

            stampset[obj.name] = reg
            noiseset[obj.name] = nmap

