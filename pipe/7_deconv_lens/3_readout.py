import progressbar
import numpy as np
import scipy
import h5py
# in some scipy versions, need to import this explicitly:
import scipy.ndimage
import sys
import os
# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')

from config import dbbudir, imgdb, settings, computer
from modules.variousfct import notify, backupfile
from modules.kirbybase import KirbyBase
from modules.deconv_utils import rebin, importSettings


pointsourcesnames = settings['pointsourcesnames']


backupfile(imgdb, dbbudir, "readout")

db = KirbyBase(imgdb, fast=True)

askquestions = settings['askquestions']
workdir = settings['workdir']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']
decpsfnames = settings['decpsfnames']
decobjname = settings['decobjname']
refimgname_per_band = settings['refimgname_per_band']
setnames = settings['setnames'] 
sample_only = settings['sample_only']
uselinks = settings['uselinks']


    
deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decfiles, decskiplists, deckeypsfuseds, ptsrccats = importSettings('lens', decname=decname, decnormfieldname=decnormfieldname)



for deckey, decskiplist, deckeyfilenum, setname, ptsrccat, \
        deckeypsfused, deckeynormused, decdir, decfile in \
            zip(deckeys, decskiplists, deckeyfilenums, setnames, ptsrccats, \
                deckeypsfuseds, deckeynormuseds, decdirs, decfiles):
                
    refimgname = refimgname_per_band[setname]
    # We select only the images that are deconvolved 
    # (and thus have a deckeyfilenum)
    images = db.select(imgdb, [deckeyfilenum], 
                              ['>0'], 
                              returnType='dict')
                              # useRegExp=True) # the sorting is not  important
    
    # We duplicate the ref image, this will be easier for the output reading.
    refimage = [image for image in images if image['imgname'] == refimgname][0]
    images.insert(0, refimage.copy()) # This copy is important !!!
    # The duplicated ref image gets number 0:
    images[0][deckeyfilenum] = 0
    
    nbimg = len(images)
    print(f"Number of images (including duplicated reference) : {nbimg}")
    

    
    # We give nbimg, so the readouttxt fct does not know 
    # that the first image is a duplication of the ref.
    with h5py.File(decfile, 'r') as f:
        psfs = np.array(f['psfs'])
        light_curves = np.array(f['light_curves'])
        data = np.array(f['stamps'])
        psfsize = psfs[0].shape[0]
        imsize = data[0].shape[0]
        resamplefac = psfsize // imsize
    print("Ok, I've read the deconvolution output.\n")
    
    if len(light_curves) == 1:
        # probably deconvolving a star:
        pointsourcesnames = ['S']
            
    
    # read params of point sources
    nbptsrcs = len(pointsourcesnames)
    print("Number of point sources :", nbptsrcs)
    print("Names of sources: ")
    for src in pointsourcesnames: print(src)
    
    # We now prepare a list of dictionnaries to be written into the database, 
    # as well as a list of fields to add to the db.
    
    newfields = []
    for src in pointsourcesnames:
        # This will contain the flux (as would be measured by aperture  
        # photometry on the original raw image):
        newfields.append({"fieldname": f"out_{deckey}_{src}_flux", 
                          "type": "float"})
        # this will contain the shot noise of the flux
        # (including sky level, psf shape)
        newfields.append({"fieldname": f"out_{deckey}_{src}_shotnoise", 
                          "type": "float"}) 
        
    negfluxes = []
    
    for ii, image in enumerate(images):
    
        print(f"{image[deckeyfilenum]} : {image['imgname']}")
    
        image["updatedict"] = {}
        # So this guy is starting at 0, even if the first image is 0001.
        outputindex = int(image[deckeyfilenum]) - 1 
    
    
        psf = psfs[ii]
    
        # We convolve it with a gaussian of width = 2.0 "small pixels".
        smallpixpsf = scipy.ndimage.filters.gaussian_filter(psf, 2.0)
        
        psf = resamplefac**2 * rebin(smallpixpsf, (imsize, imsize))
        sharpness = np.sum(psf * psf)
        
        norm = np.sum(psf)
        print(f"Equivalent pixels : {float(1.0 / sharpness):.2f}")
    
        # For info about this, see :
        # Heyer, Biretta, et al. 2004, WFPC2 Instrument Handbook, 
        # Version 9.0m (Baltimore: STScI), Chapter 6
        # http://www.stsci.edu/hst/observatory/etcs/etc_user_guide/1_3_optimal_snr.html
    
    
        for j, src in enumerate(pointsourcesnames):
    
            
            # this is the width of the "output gaussian", 
            # that we choose to be of 2 small pixels
            fwhm = 2.0 
            
            pi = 3.141592653589793
            ln2 = 0.693147180559945
    
            # mcs intensity, now starred intensity ...
            mcsint =  light_curves[j][ii] * norm
            # no multiplying by some weird constants, the starred psf
            # is already normalized to 1.
            flux = mcsint #* ( fwhm**2 / 4.0 ) * pi / (4.0 * ln2)
    
    
            # We check if the flux is positive :
            if flux < 0.0:
                negtxt = f"{image['imgname']}\t{image['datet']}, "
                negtxt += f"{src}: flux = {flux:f} "
                negfluxes.append(negtxt)
    
            # the shot noise
    
            # version 1.0 : gives to large errorbars. We are not doing aperture 
            # photometry here, but psf fitting.
            skylevel, readnoise = image["skylevel"], image['readnoise']
            shotnoise = np.sqrt(flux + ((skylevel + readnoise**2.0)/sharpness))
            shotnoise = float(shotnoise)
    
            print(f"\t{src} : \t{flux:9.2f} +/- {100 * shotnoise / flux:5.2f} %")
    
            # We *** denormalize *** :
            if image[deckeynormused] == 0.:
                image[deckeynormused] = 1e-8
            flux = flux / image[deckeynormused]
            shotnoise = shotnoise / image[deckeynormused]
    
            image["updatedict"][f"out_{deckey}_{src}_flux"] = flux
            image["updatedict"][f"out_{deckey}_{src}_shotnoise"] = float(shotnoise)
    
    print("\nI will now update the database.")
    
    
    for field in newfields:
        if field["fieldname"] not in db.getFieldNames(imgdb):
            db.addFields(imgdb, [f"{field['fieldname']}:{field['type']}"])
    
    print("New fields added.")
    
    
    # The writing itself : here we will skip the duplicated reference.
    
    widgets = [progressbar.Bar('>'), ' ', 
               progressbar.ETA(), ' ', 
               progressbar.ReverseBar('<')]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=nbimg+2).start()
    
    for i, image in enumerate(images[1:]): # we skip the duplicated reference.
        pbar.update(i)
        db.update(imgdb, [deckeyfilenum],
                         [image[deckeyfilenum]], 
                         image["updatedict"])
    
    pbar.finish()
    
    # As usual, we pack the db:
    db.pack(imgdb)
    
    notify(computer, settings['withsound'],
           f"The results of {deckey} are now in the database.")


