#
#	Read the produced out.txt
#	And write it into the database, using nice custom field names (using deckey and the source names)
#	*proud*
#	Final victory over this lovely deconv.exe output file ...
#
# For each source we insert x, y, flux = the acutal flux, calculated with a bizarre formula from the MCS intensity.
# Plus there is z1, z2, delta1, delta2 and the photonic shot noise.
#
#	WARNING  : the flux is "denormalized" by whatever normalization coeff you had used.
#	So we write raw fluxes into the db, not normalized ones !
#
import progressbar
import numpy as np
import scipy
import h5py
# in some scipy versions, need to import this explicitly:
import scipy.ndimage
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')

from config import dbbudir, imgdb, settings, computer, decfiles, settings
from modules.variousfct import notify, mcsname, fromfits, backupfile
from modules.kirbybase import KirbyBase
from modules.readandreplace_fct import readouttxt 
from modules import star
from settings_manager import importSettings


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
           decfiles, decskiplists, deckeypsfuseds, ptsrccats = importSettings('lens')


def rebin(a, newshape):
    """
    Auxiliary function to rebin ndarray data. 
    -> we put the *mean* of the orig pixels into the new ones.
    Source : http://www.scipy.org/Cookbook/Rebinning
        example usage:
        a=rand(6,4); b=rebin(a,(3,2))
        """
    shape = a.shape
    lenShape = len(shape)
    factor = np.asarray(shape)/np.asarray(newshape)
    evList = ['a.reshape('] + \
             [f'int(newshape[{int(i)}]),int(factor[{int(i)}]),' 
                 for i in range(lenShape)] + \
             [')'] + [f'.sum({int(i + 1)})' for i in range(lenShape)] + \
             [f'/factor[{int(i)}]' for i in range(lenShape)]
    return eval(''.join(evList))




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
    

    
    # The readout itself is fast :
    # intpostable, zdeltatable = readouttxt(os.path.join(decdir, "out.txt"), 
                                          # nbimg)
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
    #     newfields.append({"fieldname": f"out_{deckey}_{src.name}_x", 
    #                       "type": "float"})
    #     newfields.append({"fieldname": f"out_{deckey}_{src.name}_y", 
    #                       "type": "float"})
        # this will contain the shot noise of the flux
        # (including sky level, psf shape)
        newfields.append({"fieldname": f"out_{deckey}_{src}_shotnoise", 
                          "type": "float"}) 
        
    # newfields.append({"fieldname": f"out_{deckey}_z1", "type":"float"})
    # newfields.append({"fieldname": f"out_{deckey}_z2", "type":"float"})
    # newfields.append({"fieldname": f"out_{deckey}_delta1", "type":"float"})
    # newfields.append({"fieldname": f"out_{deckey}_delta2", "type":"float"})
    
    
    #print "Negative fluxes :"
    negfluxes = []
    

        
    for ii, image in enumerate(images):
    
        print(f"{image[deckeyfilenum]} : {image['imgname']}")
    
        image["updatedict"] = {}
        # So this guy is starting at 0, even if the first image is 0001.
        outputindex = int(image[deckeyfilenum]) - 1 
    
        # image["updatedict"][f"out_{deckey}_z1"] = zdeltatable[outputindex][0]
        # image["updatedict"][f"out_{deckey}_z2"] = zdeltatable[outputindex][1]
        # image["updatedict"][f"out_{deckey}_delta1"] = zdeltatable[outputindex][2]
        # image["updatedict"][f"out_{deckey}_delta2"] = zdeltatable[outputindex][3]
    
    
        # Reading the PSF, to calculate shotnoise:
        # psffilepath = os.path.join(decdir, f"s{image[deckeyfilenum]}.fits")
        # (mcspsf, h) = fromfits(psffilepath, verbose=False)
        psf = psfs[ii]
    
        # We rearrange the PSF quadrants so to have it in the center of the image.
        # ramcspsf = np.zeros((128, 128))
        # ramcspsf[0:64, 0:64] = mcspsf[64:128, 64:128]
        # ramcspsf[64:128, 64:128] = mcspsf[0:64, 0:64]
        # ramcspsf[64:128, 0:64] = mcspsf[0:64, 64:128]
        # ramcspsf[0:64, 64:128] = mcspsf[64:128, 0:64]
    
        # We convolve it with a gaussian of width = 2.0 "small pixels".
        smallpixpsf = scipy.ndimage.filters.gaussian_filter(psf, 2.0)
        #print "Sum of PSF : %.6f" % np.sum(smallpixpsf)
        # We rebin it
        
        psf = resamplefac**2 * rebin(smallpixpsf, (imsize, imsize))
        #print "Sum of rebinned PSF : %.6f" % np.sum(psf)
        # We calculate the sharpness :
        sharpness = np.sum(psf * psf)
        
        norm = np.sum(psf)
        print(f"Equivalent pixels : {float(1.0 / sharpness):.2f}")
    
        # For info about this, see :
        # Heyer, Biretta, et al. 2004, WFPC2 Instrument Handbook, 
        # Version 9.0m (Baltimore: STScI), Chapter 6
        # http://www.stsci.edu/hst/observatory/etcs/etc_user_guide/1_3_optimal_snr.html
    
    
        for j, src in enumerate(pointsourcesnames):
    
            # image["updatedict"][f"out_{deckey}_{src.name}_x"] = \
                        # intpostable[j][outputindex][1]
            # image["updatedict"][f"out_{deckey}_{src.name}_y"] = \
                        # intpostable[j][outputindex][2]
    
            # We calculate the flux :
    
            
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
    
    #print "\nI would now update the database."
    #proquest(askquestions)
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


