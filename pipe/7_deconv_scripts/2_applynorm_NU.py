#	
#	Here we will apply the normalisation to the g and sig images
#
from astropy.io import fits
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, computer
from modules.variousfct import proquest, mcsname, notify
from modules.kirbybase import KirbyBase
from settings_manager import importSettings

db = KirbyBase(imgdb)

askquestions = settings['askquestions']
refimgname_per_band = settings['refimgname_per_band']
setnames = settings['setnames']

# import the right deconvolution identifiers:
scenario = "normal"
if len(sys.argv)==2:
    scenario = "allstars"
    decobjname = sys.argv[1]
if settings['update']:
    scenario = "update"
    askquestions = False
    
deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decskiplists, deckeypsfuseds, ptsrccats = importSettings(scenario)

for deckey, decskiplist, deckeyfilenum, setname, \
        deckeypsfused, deckeynormused, decdir in \
            zip(deckeys, decskiplists, deckeyfilenums, setnames, \
                deckeypsfuseds, deckeynormuseds, decdirs):
    print(f"deckey : {deckey}") 
    
    refimgname = refimgname_per_band[setname]
    
     # the \d\d* is a trick to select both 0000-like, 000-like, etc.:
    images = db.select(imgdb, [deckeyfilenum], 
                              ['\d\d*'], 
                              returnType='dict', useRegExp=True, 
                              sortFields=['setname', 'mjd'])
    # we select all images that have a deckeyfilenum
    # We duplicate the ref image :
    refimage = [image for image in images if image['imgname'] == refimgname][0]
    # This copy is important!!:
    images.insert(0, refimage.copy()) 
    # The duplicated ref image gets number 1:
    images[0][deckeyfilenum] = mcsname(1)
    
    print(f"I've selected {len(images)} images (ref image is duplicated).")
    proquest(askquestions)
                  
    for image in images:
    		
    	print(image[deckeyfilenum], image['imgname'])
    	
    	mycoeff = image[deckeynormused]
    	
    	# First we handle g.fits :
    	inname = os.path.join(decdir, f"g{image[deckeyfilenum]}_notnorm.fits")
    	outname = os.path.join(decdir, f"g{image[deckeyfilenum]}.fits")
    	if os.path.exists(outname):
    		os.remove(outname)
    	
    	(a_notnorm, h) = fits.getdata(inname, header=True)
    	# No need to take care of any transpositions here, 
        # we just multiply the array by a constant.
    	a = a_notnorm * mycoeff
    	# We write the result :
    	hdu = fits.PrimaryHDU(a, h)
    	hdu.writeto(outname)
    	
    	
    	# And not sig.fits, quite similar :
    	
    	inname = os.path.join(decdir, 
                              f"sig{image[deckeyfilenum]}_notnorm.fits")
    	outname = os.path.join(decdir, 
                               f"sig{image[deckeyfilenum]}.fits")
    	if os.path.exists(outname):
    		os.remove(outname)
    	
    	(a_notnorm, h) = fits.getdata(inname, header=True)
        # yep, sigma would be multiplied but this image is 1/sigma:
    	a = a_notnorm / mycoeff 
    	# We write the result :
    	hdu = fits.PrimaryHDU(a, h)
    	hdu.writeto(outname)
    	
    
    notify(computer, settings['withsound'], 
           f"I've normalized the images for {deckey}")

