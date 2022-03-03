"""
Some plots are created in the plotdir, they should allow to check for instance the convergence of the deconvolution.

"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, plotdir
from modules.kirbybase import KirbyBase
from modules import star
from settings_manager import importSettings

db = KirbyBase(imgdb)

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
    
    # The parameters common to all sources
    
    delta1fieldname = f"out_{deckey}_delta1"
    delta2fieldname = f"out_{deckey}_delta2"
    delta1s = np.array([image[delta1fieldname] for image in images])
    delta2s = np.array([image[delta2fieldname] for image in images])
    #(delta1min, delta1max) = (np.min(delta1s), np.max(delta1s))
    #(delta2min, delta2max) = (np.min(delta2s), np.max(delta2s))
    plt.figure(figsize=(12, 12))
    ax = plt.gca()
    ax.set_aspect('equal')
    plt.scatter(delta1s, delta2s, s=1, color="blue")
    plt.xlabel("Delta 1")
    plt.ylabel("Delta 2")
    plt.title(f"Delta scatter : {deckey}")
    
    if savefigs:
        plotfilepath = os.path.join(plotdir, f"{figbase}_check_delta.pdf")
        plt.savefig(plotfilepath)
        print(f"Wrote {plotfilepath}")
    else:
        plt.show()
    
    z1fieldname = f"out_{deckey}_z1"
    z2fieldname = f"out_{deckey}_z2"
    z1s = np.array([image[z1fieldname] for image in images])
    z2s = np.array([image[z2fieldname] for image in images])
    plt.figure(figsize=(12, 12))
    plt.scatter(z1s, z2s, s=1, color="blue")
    plt.xlabel("z1")
    plt.ylabel("z2")
    plt.title(f"Z scatter : {deckey}")
    
    if savefigs:
        plotfilepath = os.path.join(plotdir, f"{figbase}_check_z.pdf")
        plt.savefig(plotfilepath)
        print(f"Wrote {plotfilepath}")
    else:
        plt.show()
    
    
    for src in ptsrcs:
        # Flux histogram
        xfieldname = f"out_{deckey}_{src.name}_x"
        yfieldname = f"out_{deckey}_{src.name}_y"
        fluxfieldname = f"out_{deckey}_{src.name}_flux"
        noisefieldname = f"out_{deckey}_{src.name}_shotnoise"
        decnormfieldname = "decnorm_" + deckey
        
        fluxes = np.array([image[fluxfieldname] for image in images])
        decnormcoeffs = np.array([image[decnormfieldname] for image in images])
        
        normfluxes = fluxes*decnormcoeffs
        
        if len(normfluxes) > 15:
            sortnormfluxes = np.sort(normfluxes)
            diffs = sortnormfluxes[1:] - sortnormfluxes[:-1]
            borderdiffs = diffs[[0, 1, 2, 3, 4, -5, -4, -3, -2, -1]]
            percentborderdiffs = borderdiffs/np.median(normfluxes)*100.0
            lowflux  = "Low  : + " + " / ".join([f"{bd:.3f}" 
                                                 for bd in percentborderdiffs[:5]]) + " %"
            highflux = "High : + " + " / ".join([f"{bd:.3f}" 
                                                 for bd in percentborderdiffs[5:]]) + " %"
            print(lowflux)
            print(highflux)
        
        plt.figure(figsize=(12, 12))
        
        (mi, ma) = (np.min(normfluxes), np.max(normfluxes))
        plt.axvline(mi, ymin=0.1, color="red")
        plt.axvline(ma, ymin=0.1, color="red")
        if len(normfluxes) > 15:
            plt.figtext(0.15, 0.85, highflux)
            plt.figtext(0.15, 0.83, lowflux)
        plt.hist(fluxes, bins=200, color=(0.6, 0.6, 0.6))
        plt.hist(normfluxes, bins=200, color=(0.3, 0.3, 0.3))
        plt.title(f"Flux histogram : {src.name + ' / ' + deckey}")
        plt.xlabel("Flux, in electrons")
        
        
        if savefigs:
            plotfilepath = os.path.join(plotdir, 
                                    f"{figbase}_check_fluxhist_{src.name}.pdf")
            plt.savefig(plotfilepath)
            print(f"Wrote {plotfilepath}")
        else:
            plt.show()
    
    
    
    
        # Lightcurve
        
        plt.figure(figsize=(15, 8))
        
        decfilenums = np.array(list(map(int, [image[deckeyfilenum] 
                                             for image in images])))
        
        (xmi, xma) = (np.min(decfilenums), np.max(decfilenums))
        (ymi, yma) = (np.min(normfluxes) - 0.5*np.std(normfluxes), 
                      np.max(normfluxes) + 0.5*np.std(normfluxes))
        
        plt.plot(decfilenums, normfluxes, marker=".", linestyle="none")
        plt.title(f"Lightcurve : {src.name + ' / ' + deckey}")
        plt.xlabel("MCS files")
        plt.ylabel("Normalized flux")
        plt.xlim((xmi - 10.0, xma + 10.0))
        plt.ylim((ymi, yma))
        
        
        
        if savefigs:
            plotfilepath = os.path.join(plotdir, 
                                  f"{figbase}_check_fluxlc_{src.name}.pdf")
            plt.savefig(plotfilepath)
            print(f"Wrote {plotfilepath}")
        else:
            plt.show()

    

    




