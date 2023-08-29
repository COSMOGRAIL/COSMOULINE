"""
Now that the coeffs are in the db, you might want to plot curves
(very similar to those made by the normalize script), but for other stars,
not involved in the normalization.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')
from config import imgdb, settings, plotdir
from modules.kirbybase import KirbyBase


normname = settings['normname']
setnames = settings['setnames']
allnormsources = settings['normsources']

db = KirbyBase(imgdb)


for setname, normsources in zip(setnames, allnormsources):
    print("I will plot lightcurves using normalization coefficient called :")
    print(normname)
    print("for the sources")
    for normsource in normsources:
        print(normsource)
    
    
   
    allimages = db.select(imgdb, ['gogogo', 'treatme', 'setname'], 
                                 [True, True, setname], 
                                 returnType='dict', 
                                 sortFields=['mjd'])
    print(f"{len(allimages)} images in total.")
    
    
    for normsource in normsources:
        deckey = normsource[0]
        sourcename = normsource[1]
        print(deckey)
        
        deckeyfilenumfield = "decfilenum_" + deckey
        fluxfieldname = "out_" + deckey + "_S_flux"
        errorfieldname = "out_" + deckey + "_S_shotnoise"
        decnormfieldname = "decnorm_" + deckey
        
        images = [image for image in allimages 
                         if image[deckeyfilenumfield] != None]
        print(f"{len(images)} images")
    
        fluxes = np.array([image[fluxfieldname] for image in images])
        errors = np.array([image[errorfieldname] for image in images])
        decnormcoeffs = np.array([image[decnormfieldname] for image in images])
        airmasses = np.array([image["airmass"] for image in images])
        skylevels = np.array([image["skylevel"] for image in images])
    
        normcoeffs = np.array([image[normname] for image in images])
        
        normfluxes = fluxes*normcoeffs
        normerrors = errors*normcoeffs
        ref = np.median(normfluxes)
        
        mhjds = np.array([image["mhjd"] for image in images])
        
        plt.figure(figsize=(15,15))
    
        plt.errorbar(mhjds, normfluxes/ref, yerr=normerrors/ref, 
                                              ecolor=(0.8, 0.8, 0.8), 
                                              linestyle="None", 
                                              marker="None")
        plt.scatter(mhjds, normfluxes/ref, s=12, 
                                             c=airmasses, 
                                             vmin=1.0, vmax=1.5, 
                                             edgecolors='none', 
                                             zorder=20)
        
    
        plt.title(f"Source {sourcename}, {deckey}, normalized with {normname}")
        plt.xlabel("MHJD")
        plt.ylabel("Flux in electrons / median")
        plt.grid(True)
        #plt.ylim(0.95, 1.05)
        plt.ylim(0.90, 1.1)
        plt.xlim(np.min(mhjds), np.max(mhjds))
        
        cbar = plt.colorbar(orientation='horizontal')
        cbar.set_label('Airmass') 
        #cbar.set_label('Raw skylevel [electrons]')
        
        if settings['savefigs']:
            fname = f"norm_{setname}_{normname}_normflux_{sourcename}.pdf"
            plotfilepath = os.path.join(plotdir, fname)
            plt.savefig(plotfilepath)
            print(f"Wrote {plotfilepath}")
        else:
            plt.show()
