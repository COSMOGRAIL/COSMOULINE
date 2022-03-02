"""
Look for strange flux values...

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
from config import imgdb, settings
from modules.kirbybase import KirbyBase
from modules import star
from settings_manager import importSettings

db = KirbyBase()

askquestions = settings['askquestions']
decnormfieldname = settings['decnormfieldname']
setnames = settings['setnames']
savefigs = settings['savefigs']

# import the right deconvolution identifiers:
scenario = "normal"
if len(sys.argv)==2:
    scenario = "allstars"
if settings['update']:
    scenario = "update"
    askquestions = False
    
deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decskiplists, deckeypsfuseds, ptsrccats = importSettings(scenario)
           
           
for deckey, decskiplist, deckeyfilenum, setname, ptsrccat, \
        deckeypsfused, deckeynormused, decdir in \
            zip(deckeys, decskiplists, deckeyfilenums, setnames, ptsrccats, \
                deckeypsfuseds, deckeynormuseds, decdirs):
    figbase = deckey
    
    images = db.select(imgdb, [deckeyfilenum], 
                              ['\d\d*'], 
                              returnType='dict', 
                              useRegExp=True, 
                              sortFields=['setname', 'mhjd'])
    
    ptsrcs = star.readmancat(ptsrccat)
    nbptsrcs = len(ptsrcs)
    print("Number of point sources :", nbptsrcs)
    print("Names of sources : ")
    for src in ptsrcs: 
        print(src.name)
    
    
    
    for src in ptsrcs:
    
        fluxfieldname = "out_" + deckey + "_" + src.name + "_flux"
        noisefieldname = "out_" + deckey + "_" + src.name + "_shotnoise"
        decnormfieldname = "decnorm_" + deckey
        
        fluxes = np.array([image[fluxfieldname] for image in images])
        decnormcoeffs = np.array([image[decnormfieldname] for image in images])
        
        normfluxes = fluxes*decnormcoeffs
        
        """
        for i, flux in enumerate(fluxes):
            if flux < 0.0:
                print "Negative flux: %.3f " % (flux)
                
        for i, norm in enumerate(decnormcoeffs):
            if norm < 0.0:
                print "Negative normcoeff: %.3f " % (norm)
                
        for i, normflux in enumerate(normfluxes):
            if normflux < 0.0:
                print "Negative normalized flux: %.3f " % (normflux)
        """
        
        rejlines = []    
        rejectimages = [image for image in images if image[fluxfieldname] < 0.0]
        rejlines.extend("%s\t\t%s" % (image["imgname"], "flux %s = %.3f" % (src.name, image[fluxfieldname])) for image in rejectimages)
        rejectimages = [image for image in images if image[decnormfieldname] < 0.0]
        rejlines.extend(f"{image['imgname']}\t\t{'normcoeff = %.3f' % image[decnormfieldname]}" for image in rejectimages)
        
        if len(rejlines) == 0:
            print(f"# All images have positive {src.name} fluxes and normcoefficients.")
        
        else:
            print(f"# These images have negative {src.name} fluxes and/or a negative normcoefficient :")
            print("\n".join(rejlines))
            print("# Please put them on your kicklist!")
        
