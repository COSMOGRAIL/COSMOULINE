"""
We use cosmics.py to locate cosmics in the extracted images.
We do not clean them, but mask them in the corresponding sigma images.
We do not update the database.

OUTPUT:
    - an hdf5 file containing all the cosmic masks (one per image and per star)
      at `psfdir / cosmics_masks.h5`.
    - a json file containing the description of each cosmic (useful for plots)
      at `psfdir / cosmics_labels.json`. 
      
Unlike the case of the user masking in 1_prepare.py, we do not mask
the stars directly. Instead we store the cosmic masks in the separate
file mentioned above. (This is fully automatic, and hence can go wrong
                       -- we are being careful.)
"""

import sys
import os
from   pathlib import Path
import multiprocessing
import numpy as np
import h5py
import json
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    pass
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
sys.path.append('..')
from config import settings, psfstarcat, psfkeyflag, imgdb, psfdir,\
                   computer
from modules.variousfct import proquest, notify
from modules.kirbybase import KirbyBase
from modules import cosmics
# weird looking import for star: that is because pickle
# makes a difference between "from a import b" and "import a.b as b":
# it will refuse to pickle the former case sometimes. 
import modules.star as star


askquestions = settings['askquestions']
maxcores = settings['maxcores']
withsound = settings['withsound']
psfname = settings['psfname']
update = settings['update']
cosmicssigclip = settings['cosmicssigclip']

psfdir = Path(psfdir)

starsh5 = h5py.File(psfdir / 'stars.h5', 'r')
noiseh5 = h5py.File(psfdir / 'noisemaps.h5', 'r')

psfstars = star.readmancat(psfstarcat)

def findcosmics(image, psfstars, sigclip, sigfrac, objlim):

    pssl = image['skylevel']
    gain = image['gain']
    # satlevel = image['saturlevel']*gain*maxpixelvaluecoeff
    satlevel = -1.0
    readnoise = image['readnoise']
    
    stars = starsh5[image['imgname']]


    cosmicmasks = []
    cosmiclabels = []
    
    for i in range(len(psfstars)):
        
        a = stars[i]

        # Creating the object :
        c = cosmics.cosmicsimage(a, pssl=pssl, gain=gain, readnoise=readnoise, 
                                    sigclip=sigclip, sigfrac=sigfrac,
                                    objlim=objlim, satlevel=satlevel,
                                    verbose=False)  
                                    # I put a correct satlevel instead of -1, 
                                    # to treat VLT images.


        c.run(maxiter=3)

        cosmicmask = c.getdilatedmask(size=5)
        cosmiclist = c.labelmask()
        
        cosmicmasks.append(cosmicmask)
        cosmiclabels.append(cosmiclist)
        

    return np.array(cosmicmasks), cosmiclabels
    # cosmicsh5[image['imgname']+'_labels'] = cosmiclist


def multi_findcosmics(args):
   return findcosmics(*args)

def main():
    
    ###########
    # make these two switches local variables since they are potentially
    # modified within this function.
    askquestions = settings['askquestions']
    withsound = settings['withsound']
    
    
    # more settings:
    sigclip = cosmicssigclip
    sigfrac = 0.3
    # 5.0 seems good for VLT. 1.0 works fine with Euler. Change with caution
    objlim = 3.0

    ###########

    # Select images to treat
    db = KirbyBase(imgdb)

    if settings['thisisatest'] :
        print("This is a test run.")
        images = db.select(imgdb, ['gogogo', 'treatme', 'testlist' ,psfkeyflag], 
                                  [True, True, True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
    elif settings['update']:
        print("This is an update")
        images = db.select(imgdb, ['gogogo', 'treatme', 'updating', psfkeyflag], 
                                  [True, True, True, True],
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
        askquestions = False
        withsound = False
    else :
        images = db.select(imgdb, ['gogogo', 'treatme', psfkeyflag], 
                                  [True, True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])


    print("I will find cosmics of %i images." % len(images))

    ncorestouse = multiprocessing.cpu_count()
    if maxcores > 0 and maxcores < ncorestouse:
        ncorestouse = maxcores
        print(f"maxcores = {maxcores}")
    print(f"For this I will run on {ncorestouse} cores.")
    proquest(askquestions)

    for i, img in enumerate(images):
        # We do not write this into the db, it's just for this particular run.
        img["execi"] = (i+1) 

    # We see how many stars we have :
    psfstars = star.readmancat(psfstarcat)

    args = [(im, psfstars, sigclip, sigfrac, objlim) for im in images]
    pool = multiprocessing.Pool(processes=ncorestouse)
    results = pool.map(multi_findcosmics, args)
    
    labelfile = psfdir / 'cosmics_labels.json'
    labels = {im['imgname']:j[1] for im, j in zip(images, results)}
    with open(labelfile, 'w') as fp:
        json.dump(labels, fp)
    
    with h5py.File(psfdir / 'cosmics_masks.h5', 'w') as cosmicsh5:
        for res, image in zip(results, images):
            mask, _ = res
            cosmicsh5[image['imgname']+'_mask'] = mask
        

    notify(computer, withsound, f"Cosmics masked for psfname {psfname}.")

if __name__ == '__main__':
    main()