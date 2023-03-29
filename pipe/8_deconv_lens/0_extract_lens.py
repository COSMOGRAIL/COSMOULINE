#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 02:37:55 2023

@author: fred
"""


import sys
import os
from pathlib import Path
import numpy as np
import h5py
from astropy.io import fits
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    pass
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
sys.path.append('..')
from config import dbbudir, imgdb, settings, extract_template_filename, \
                   alidir, extractexe, computer, photomstarscat, extracteddir
from modules.variousfct import backupfile, proquest, readmancat, mterror,\
                               notify, copyorlink
from modules.kirbybase import KirbyBase
from modules import cosmics, star

askquestions = settings['askquestions']
withsound = settings['withsound']
workdir = Path(settings['workdir'])
uselinks = settings['uselinks']
refimgname_per_band = settings['refimgname_per_band']

maxcores = settings['maxcores']
psfname = settings['psfname']
update = settings['update']
cosmicssigclip = settings['cosmicssigclip']

alidir = Path(alidir)




def extractRegionsFromImages(images, regions, storagefile):
    """
    image: database entry (dictionary)
    regions: dic of tuples: {obj1: (xmin, xmax, ymin, ymax), obj2:...}
    
    extracts stamps: meaning reads the fits file, computes noise, saves stamps
    as stacks of 2D arrays for each region.

    """
    extracted = {obj:[] for obj in regions.keys()}
    extractednoise = {obj:[] for obj in regions.keys()}
    for image in images:
        alifile = alidir / f"{image['imgname']}_ali.fits"
        
        # aligned images are in e-
        alidata = fits.getdata(alifile)
        
        # noise map
        stddev = image['prealistddev']
        noise = np.zeros_like(alidata) + stddev + np.sqrt(np.abs(alidata))
        
        # more info for cosmics later:
        pssl = image['skylevel']
        gain = image['gain']
        # satlevel = image['saturlevel']*gain*maxpixelvaluecoeff
        satlevel = -1.0
        readnoise = image['readnoise']
        
        sigclip = cosmicssigclip
        sigfrac = 0.3
        # 5.0 seems good for VLT. 1.0 works fine with Euler. Change with caution
        objlim = 3.0
        
        for obj, coords in regions.items():
            coords = (int(e) for e in coords)
            (xm, xM, ym, yM) = coords
            datastamp = alidata[ym:yM, xm:xM] 
            c = cosmics.cosmicsimage(datastamp, pssl=pssl, gain=gain, 
                                     readnoise=readnoise, 
                                     sigclip=sigclip, sigfrac=sigfrac,
                                     objlim=objlim, satlevel=satlevel,
                                     verbose=False)  
            c.run(maxiter=3)
    
            cosmicmask = c.getdilatedmask(size=5)
            
            noisestamp = noise[ym:yM, xm:xM]
            noisestamp[cosmicmask] = 1e8
            
            
            h5key = f"{obj}_{image['imgname']}"
            h5keynoise = h5key + '_noise'
            
            with h5py.File(storagefile, 'r+') as f:
                for key, array in zip((h5key, h5keynoise), (datastamp, noisestamp)):
                    if key in f.keys():
                        del f[key]
                    f[key] = array
        
            
            
db = KirbyBase(imgdb)

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], 
                                            ['*'], ['setname'])])



regions = {}
psfstampsize = settings['psfstampsize']
lensregion = settings['lensregion']
hh = psfstampsize // 2

# the lens
lenscoords = [lensreg.split(':') for lensreg in lensregion.split(',')]

xlens = (float(lenscoords[0][0][1:]) + float(lenscoords[0][1])) // 2
ylens = (float(lenscoords[1][0]) + float(lenscoords[1][1][:-1])) // 2

regions['lens'] =  (xlens-hh, xlens+hh, ylens-hh, ylens+hh)


for setname in usedsetnames:
    bandrefimage = refimgname_per_band[setname]
    if settings['thisisatest'] :
        print("This is a test run.")
        images = db.select(imgdb, ['gogogo','treatme','testlist','setname'], 
                                  [True, True, True, setname], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
    else :
        images = db.select(imgdb, ['gogogo', 'treatme', 'setname'], 
                                  [True, True, setname], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
    
    nbrofimages = len(images)
    
    
    
    print("I will extract from", nbrofimages, "images.")
    
    extractedfile = extracteddir / f'{setname}_extracted.h5'
    if not extractedfile.exists():
        with h5py.File(extractedfile, 'w') as f:
            pass
        
    extractRegionsFromImages(images, regions, extractedfile)



