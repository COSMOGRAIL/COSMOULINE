"""
We use cosmics.py to locate cosmics in the extracted images.
We do not clean them, but mask them in the corresponding sigma images.
We do not update the database.

OUTPUT:
    - an hdf5 file containing all the cosmic masks (one per image and per star)
      at `extracteddir / cosmics_masks.h5`.
    - a json file containing the description of each cosmic (useful for plots)
      at `extracteddir / cosmics_labels.json`. 
      
Unlike the case of the user masking in 2_manual_masking.py, we do not mask
the stars directly. Instead we store the cosmic masks in the separate
file mentioned above. (Because this is fully automatic and can hence go wrong
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
from config import settings, imgdb, computer, cosmicslabelfile, extracteddir

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
update = settings['update']
cosmicssigclip = settings['cosmicssigclip']



regionsfile = h5py.File(extracteddir / 'regions.h5', 'r+')


def findcosmics(imgdbentry, name, sigclip, sigfrac, objlim):
    """
    imgdbentry: dictionary with the database row of the image at hand
    name: current object name (string)
    sigclip, sigfrac, objlim: floats, params of the cosmics routine.
    """
    pssl = imgdbentry['skylevel']
    gain = imgdbentry['gain']
    satlevel = -1.0
    readnoise = imgdbentry['readnoise']
    imgname = imgdbentry['imgname']
        
    # now we load the stamp of the object.
    a = regionsfile[imgname]['stamps'][name][()]

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


    return imgdbentry, name, cosmicmask, cosmiclist


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
    objlim = 1.0

    ###########

    # Select images to treat
    db = KirbyBase(imgdb)

    if settings['thisisatest'] :
        print("This is a test run.")
        images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], 
                                  [True, True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
    elif settings['update']:
        print("This is an update")
        images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                                  [True, True, True],
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
        askquestions = False
        withsound = False
    else :
        images = db.select(imgdb, ['gogogo', 'treatme'], 
                                  [True, True], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])


    print("I will find cosmics of %i images." % len(images))

    ncorestouse = multiprocessing.cpu_count()
    if maxcores > 0 and maxcores < ncorestouse:
        ncorestouse = maxcores
        print(f"maxcores = {maxcores}")
    print(f"For this I will run on {ncorestouse} cores.")
    proquest(askquestions)


    args = []
    for i, img in enumerate(images):
        # let us prepare the run by assembling the arguments
        
        # objects in this image:
        objects = regionsfile[img['imgname']]['stamps'].keys()
        for obj in objects:
            # one stamp per object.
            args.append((img, obj, sigclip, sigfrac, objlim))




    pool = multiprocessing.Pool(processes=ncorestouse)
    results = pool.map(multi_findcosmics, args)
    
    # now writing our results.

    labels = {}
    
    for res in results:
        imgdbentry, name, mask, label = res
        imgname = imgdbentry['imgname']
        if not name in regionsfile[imgname]['cosmicsmasks']:
            regionsfile[imgname]['cosmicsmasks'][name] = mask
        else:
            regionsfile[imgname]['cosmicsmasks'][name][...] = mask
        
        labels[imgname + '_' + name] = label

    with open(cosmicslabelfile, 'w') as fp:
        json.dump(labels, fp)

    notify(computer, withsound, f"Cosmics masked.")

if __name__ == '__main__':
    main()

regionsfile.close()
