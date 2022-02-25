"""
We use cosmics.py to locate cosmics in the extracted images.
We do not clean them, but mask them in the corresponding sigma images.
We do not update the database.
"""
import multiprocessing
import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import settings, psfstarcat, psfkeyflag, imgdb, psfdir,\
                   computer
from modules.variousfct import proquest, notify, writepickle
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

psfstars = star.readmancat(psfstarcat)

def findcosmics(image, psfstars, sigclip, sigfrac, objlim):
    imgpsfdir = os.path.join(psfdir, image['imgname'])
    print("Image %i : %s" % (image["execi"], imgpsfdir))

    os.chdir(os.path.join(imgpsfdir, "results"))

    pssl = image['skylevel']
    gain = image['gain']
    # satlevel = image['saturlevel']*gain*maxpixelvaluecoeff
    satlevel = -1.0
    readnoise = image['readnoise']
    print("Gain %.2f, PSSL %.2f, Readnoise %.2f" % (gain, pssl, readnoise))

    for i in range(len(psfstars)):
        starfilename = "star_%03i.fits" % (i + 1)
        sigfilename = "starsig_%03i.fits" % (i + 1)
        origsigfilename = "origstarsig_%03i.fits" % (i + 1)
        starmaskfilename = "starmask_%03i.fits" % (i + 1)
        starcosmicspklfilename = "starcosmics_%03i.pkl" % (i + 1)

        # We reset everyting
        if os.path.isfile(origsigfilename):
            # Then we reset the original sigma image :
            if os.path.isfile(sigfilename):
                os.remove(sigfilename)
            os.rename(origsigfilename, sigfilename)

        if os.path.isfile(starmaskfilename):
            os.remove(starmaskfilename)
        if os.path.isfile(starcosmicspklfilename):
            os.remove(starcosmicspklfilename)

        # We read array and header of that fits file :
        (a, h) = cosmics.fromfits(starfilename, verbose=False)

        # Creating the object :
        c = cosmics.cosmicsimage(a, pssl=pssl, gain=gain, readnoise=readnoise, 
                                    sigclip=sigclip, sigfrac=sigfrac,
                                    objlim=objlim, satlevel=satlevel,
                                    verbose=False)  
                                    # I put a correct satlevel instead of -1, 
                                    # to treat VLT images.

        # print pssl, gain, readnoise, sigclip, sigfrac, objlim

        c.run(maxiter=3)

        ncosmics = np.sum(c.mask)

        # We write the mask :
        cosmics.tofits(starmaskfilename, c.getdilatedmask(size=5), 
                       verbose=False)

        # And the labels (for later png display) :
        cosmicslist = c.labelmask()
        writepickle(cosmicslist, starcosmicspklfilename, verbose=False)

        # We modify the sigma image, but keep a copy of the original :
        os.rename(sigfilename, origsigfilename)
        (sigarray, sigheader) = cosmics.fromfits(origsigfilename, 
                                                 verbose=False)
        sigarray[c.getdilatedmask(size=5)] = 1.0e8
        cosmics.tofits(sigfilename, sigarray, sigheader, verbose=False)

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
    db = KirbyBase()

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
    pool.map(multi_findcosmics, args)

    notify(computer, withsound, f"Cosmics masked for psfname {psfname}.")

if __name__ == '__main__':
    main()