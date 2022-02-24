"""
Calculation of first guess normalization coefficients.
You can relaunch this with other stars to test different combinations if you want.


This is a bit simplistic : here we *do* rely on the reference image as a reference.
This is well adapted to calculate such coefficients over different telescopes etc.
Of course the reference image will have a coeff of 1.0

We use FLUX_AUTO

Later we will do something more sophisticated for the renormalization.


By the way, from 2022 we introduce some changes:
    "setname" is not associated with a filter, or a band.
    We process each subset of images with the same "setname" separately.
    Therefore, each band will have its own photometric reference image. 

"""
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
from config import alidir, imgdb, dbbudir, settings, normstarscat
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest, backupfile
from modules import star


askquestions = settings['askquestions']
identtolerance = settings['identtolerance']

# As we will tweak the database, do a backup first
backupfile(imgdb, dbbudir, 'calccoeff')

db = KirbyBase()



def simplemediancoeff(refidentstars, identstars):
    """
    calculates a simple (but try to get that better ... it's pretty good !)
    multiplicative coeff for each image
    "calc one coef for each star and take the median of them"
    coef = reference / image
    """
    
    coeffs = []
    for refstar in refidentstars:
        for star_ in identstars:
            if refstar.name != star_.name:
                continue
            coeffs.append(refstar.flux/star_.flux)
            break
    
    coeffs = np.array(coeffs)
    if len(coeffs) > 0:
        return len(coeffs), float(np.median(coeffs)), float(np.std(coeffs)), \
               float(np.max(coeffs) - np.min(coeffs))
    else:    
        return 0, 1.0, 99.0, 99.0
    
    

# from now, we need one reference image per band. We make sure that
# they are indeed set in settings:
refimgname_per_band = settings['refimgname_per_band']
bandswithref = set(refimgname_per_band.keys())

usedsetnames = set([x[0] for x in db.select(imgdb, ['recno'], 
                                                   ['*'], 
                                                   ['setname'])])

        
        
if not usedsetnames == bandswithref:
    print("You are missing some reference imaging for each band!")
    print(f"My database has these bands: {usedsetnames},")
    print(f"But your settings.py file only mentions these: {bandswithref}")
    print("You can either remove the unwanted bands from the database, ")
    print("or add reference images in settings.py (variable refimgname_per_band)")


# we prepare the database
if "nbrcoeffstars" not in db.getFieldNames(imgdb) :
    print("I will add some fields to the database.")
    proquest(askquestions)
    db.addFields(imgdb, ['nbrcoeffstars:int', 'maxcoeffstars:int', 
                         'medcoeff:float', 'sigcoeff:float', 'spancoeff:float'])

# we read the handwritten star catalog
normstars = star.readmancat(normstarscat)
if len(normstars) == 0:
    print("No norm star read from catalog!!!")
    sys.exit()
for s in normstars:
    print(f"{s.name} {s.x:.01f} {s.y:.01f}")

for setname in usedsetnames:

    if settings['update']:
        print("This is an update.")
        images = db.select(imgdb, ['gogogo', 'treatme', 'updating', 'setname'], 
                                  [True, True, True, setname], 
                                  returnType='dict')
        askquestions = False
    else:
        images = db.select(imgdb, ['gogogo', 'treatme', 'setname'], 
                                  [True, True, setname], 
                                  returnType='dict')
    nbrofimages = len(images)
    
    
    refimgnameband = refimgname_per_band[setname]
    
    
    print("Checking reference image ...")
    refsexcat = os.path.join(alidir, refimgnameband + ".alicat")
    refcatstars = star.readsexcat(refsexcat, maxflag=16,
                                  propfields=["FLUX_APER", "FLUX_APER1", 
                                              "FLUX_APER2", "FLUX_APER3", 
                                              "FLUX_APER4"])
    id = star.listidentify(normstars, refcatstars, tolerance=identtolerance,                           
                           onlysingle=True, 
                           verbose=True) 
    refidentstars = id["match"]
    # now refidentstars contains the same stars as normstars, but with sex fluxes.
    
    
    
    if len(refidentstars) != len(normstars):
        print("Not all normstars identified in sextractor cat of reference image !")
        print("If you are confident that all the stars are in that reference image,")
        print("Consider increasing identtolerance slightly in settings.py")
        sys.exit()
    
    # the maximum number of possible stars that could be used
    maxcoeffstars = len(normstars)
    print("Number of coefficient stars :", maxcoeffstars)
    nbrofimages = len(images)
    print("I will treat", nbrofimages, "images.")
    proquest(askquestions)
    
    
    for i, image in enumerate(images):
        print("- "*30)
        print(i+1, "/", nbrofimages, ":", image['imgname'])
        
        # the catalog we will read
        sexcat = os.path.join(alidir, image['imgname'] + ".alicat")
        
        # read sextractor catalog
        catstars = star.readsexcat(sexcat, maxflag = 0, posflux = True)
        if len(catstars) == 0:
            print("No stars in catalog !")
            db.update(imgdb, ['recno'], 
                             [image['recno']], 
                             {'nbrcoeffstars': 0, 'maxcoeffstars': maxcoeffstars, \
                              'medcoeff': 1.0, 'sigcoeff': 99.0, 'spancoeff': 99.0})
            continue
            
        # cross-identify the stars with the handwritten selection
        identstars = star.listidentify(normstars, catstars, 5.0)["match"]
    
        # calculate the normalization coefficient
        nbrcoeff, medcoeff, sigcoeff, spancoeff = simplemediancoeff(refidentstars, 
                                                                    identstars)
        
        print("nbrcoeff :", nbrcoeff)
        print("medcoeff :", medcoeff)
        print("sigcoeff :", sigcoeff)
        print("spancoeff :", spancoeff)
        
        db.update(imgdb, ['recno'], 
                         [image['recno']], 
                         {'nbrcoeffstars': nbrcoeff, 'medcoeff': medcoeff, \
                          'maxcoeffstars': maxcoeffstars, 'sigcoeff': sigcoeff, \
                          'spancoeff': spancoeff})
    
    db.pack(imgdb) # to erase the blank lines
    
    print("Done.")
    
    
