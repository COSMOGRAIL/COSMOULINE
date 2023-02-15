#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:46:31 2023

@author: fred dux


This file 
 - selects all the images matching our settings.py configuration,
 - extracts the PSF stars from them
 - at the same time, builds a noise map for each star / image
 - helps the user create masks with ds9
 - applies the created masks to our noise maps. 

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
from config import configdir, settings, psfkey, psfstarcat, imgdb, dbbudir,\
                   psfdir, psfkeyflag, alidir
from modules.variousfct import proquest, backupfile, mterror
from modules import star
from modules import ds9reg
from modules.kirbybase import KirbyBase


psfstampsize = settings['psfstampsize']
alidir = Path(alidir)
psfdir = Path(psfdir)

update = settings['update']
askquestions = settings['askquestions']
refimgname = settings['refimgname']

db = KirbyBase(imgdb)


print("psfkey =", psfkey)

print("Reading psf star catalog ...")
psfstars = star.readmancat(psfstarcat)
print("You want to use stars :")
for s in psfstars:
    print(s.name)


if settings['update']:
    askquestions = False

proquest(askquestions)

backupfile(imgdb, dbbudir, "prepare_" + psfkey)

# Then, we inpect the current situation.
# Check if the psfdir already exists

if os.path.isdir(psfdir):
    print("This psfdir already exists. I will add or rebuild psfs in this set.")
    print("psfdir :", psfdir)
    proquest(askquestions)
    
    # Check if the psfkeyflag is in the database, to be sure it exists.
    if psfkeyflag not in db.getFieldNames(imgdb) :
        raise mterror("...but your corresponding psfkey is not in the database!")
    
    if settings['thisisatest']:
        print("This is a test !")
        print("So you want to combine/replace an existing psf with a test-run.")
        proquest(askquestions)
        
else :
    print("I will create a NEW psf.")
    print("psfdir :", psfdir)
    proquest(askquestions)
    if psfkeyflag not in db.getFieldNames(imgdb) :
        db.addFields(imgdb, ['%s:bool' % psfkeyflag])
    else:
        raise mterror("...funny: the psfkey was in the DB! Please clean psfdir and psfkey!")
    os.mkdir(psfdir)    


# We select the images, according to "thisisatest".
# Note that only this first script of the psf construction looks at this :
# the next ones will simply  look for the psfkeyflag in the database !

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


print("I will treat %i images." % len(images))
proquest(askquestions)




# Format the psf stars catalog
nbrpsf = len(psfstars)
starscouplelist = [(int(s.x), int(s.y)) for s in psfstars]


starsarray = h5py.File(psfdir / 'stars.h5', 'w')
noisearray = h5py.File(psfdir / 'noisemaps.h5', 'w')

for i,image in enumerate(images):
    print(40*"- ")
    print("%i / %i : %s" % (i+1, len(images), image['imgname']))
    
    alifile = alidir / f"{image['imgname']}_ali.fits"
    
    # aligned images are in e-
    alidata = fits.getdata(alifile)
    
    # noise map
    stddev = image['stddev']
    noise = np.zeros_like(alidata) + stddev + np.sqrt(np.abs(alidata))
    
    # extract the stars
    h = psfstampsize // 2
    stars = np.array([alidata[y-h:y+h, x-h:x+h] for x,y in starscouplelist])
    nmaps = np.array([noise[y-h:y+h, x-h:x+h] for x,y in starscouplelist])
    
    # now we mask.
    starsarray[image['imgname']] = stars
    noisearray[image['imgname']] = nmaps
    
    
    # and we update the database with a "True" for field psfkeyflag :
    db.update(imgdb, ['recno'], [image['recno']], [True], [psfkeyflag])


# now, deal with the masking
if refimgname in starsarray:
    
    print("You can now open these files with DS9 to build your mask (optional).")
    print("Don't mask cosmics, only companion stars !")
    print("Save your region files respectively here :")
    
    maskfilepaths = [os.path.join(configdir, "%s_mask_%s.reg" % (psfkey, name)) 
                                        for name in [s.name for s in psfstars]]
    print("\n".join(maskfilepaths))
    
    print("If asked, use physical coordinates and DS9 (or REG) file format.")
else:
    raise RuntimeError('The reference image was not found in your PSF set of images.')

if not update:
    text = 5*"\n"
    text += "Now we need to mask our PSF star stamps from contaminant stars.\n"
    text += "Want me to open DS9 on each star so that you can build a mask?\n"
    text += "Btw for each star the path to where the mask needs to be saved\n"
    text += "will be copied to your clipboard.   So, open DS9? (yes/no) "
    if input(text) == 'yes':
        tmpdirr = TemporaryDirectory()
        tmpdir = Path(tmpdirr.name)
        
        for stardata, maskfile in zip(starsarray[refimgname], maskfilepaths):
            # copy the mask file to the clipboard:
            pyperclip.copy(maskfile)
            print(f'save your region file to \n{maskfile}')
            # store star data in file:
            mfname = Path(maskfile).name
            starfile = tmpdir / (mfname + '.fits')
            fits.writeto(starfile, stardata)
            # open with ds9
            call(['ds9', starfile])
            # now mask the companion stars in ds9, and save the regions
            # to the file copied in the cilpboard.
            
        tmpdirr.cleanup()


# ok, building the masks
for i, s in enumerate(psfstars):
    print('---------------PSF STAR------------------')
    print(s.name)
    print('-----------------------------------------')
    
    s.filenumber = (i+1)
    possiblemaskfilepath = os.path.join(configdir, f"{psfkey}_mask_{s.name}.reg")
    print('mask file path is: ', possiblemaskfilepath)
    if os.path.exists(possiblemaskfilepath):

        s.reg = ds9reg.regions(psfstampsize, psfstampsize) 
        s.reg.readds9(possiblemaskfilepath, verbose=False)
        s.reg.buildmask(verbose = False)
        
        print("You masked %i pixels of star %s." % (np.sum(s.reg.mask), s.name))
    else:
        print("No mask file for star %s." % (s.name))
        
        


# now, applying the masks:
print('Applying the masks!')
for i, image in enumerate(images):
    
    print("%i : %s" % (i+1, image['imgname']))
    
    for s, sigarray in zip(psfstars, noisearray[image['imgname']]):
        
        if not hasattr(s, 'reg'): # If there is no mask for this star
            continue

        sigarray[s.reg.mask] = 1.0e8
    

print("- " * 40)

# now, we finalize our stars and noise maps by closing the files.
starsarray.close()
noisearray.close()

# the decoy in case someone uses the old KirbyBase... one day to be removed.
db.pack(imgdb)
