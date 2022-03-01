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
from config import imgdb, settings, configdir, computer
from modules.variousfct import proquest, mcsname, notify
from modules.kirbybase import KirbyBase

db = KirbyBase()

askquestions = settings['askquestions']
workdir = settings['workdir']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']
decpsfnames = settings['decpsfnames']
decobjname = settings['decobjname']
refimgname = settings['refimgname']
refimgname_per_band = settings['refimgname_per_band']
setnames = settings['setnames']

# this script can be ran with an object to deconvolve as an argument.
# in this case, force the rebuild of all the keys
if len(sys.argv) == 2:
    print("You are running the deconvolution on all the stars at once.")
    print("Current star : " + sys.argv[1])
    decskiplists, deckeyfilenums, deckeypsfuseds  = [], [], []
    deckeynormuseds, decdirs, deckeys = [], [], []
    for setname in setnames:
        # here we rebuild all the keys that track our deconvolution.
        # (this is normally done in config.py)
        decobjname = sys.argv[1]
        deckey  = f"dec_{decname}_{decobjname}_{decnormfieldname}_"
        deckey += "_".join(decpsfnames)
        deckeys.append(deckey)
        decskiplist = os.path.join(configdir, deckey + "_skiplist.txt")
        decskiplists.append(decskiplist)
        deckeyfilenum = "decfilenum_" + deckey
        deckeyfilenums.append(deckeyfilenum)
        deckeypsfused = "decpsf_" + deckey
        deckeypsfuseds.append(deckeypsfused)
        deckeynormused = "decnorm_" + deckey
        deckeynormuseds.append(deckeynormused)
        decdir = os.path.join(workdir, deckey)
        decdirs.append(decdir)



# moreover, if this is an udpate: read the config file produced by the
# original deconvolution.
# (well this is a bit confusing, as deconv_config_update mixes
# settings that are stored both in config.py and settings.py. 
# something to improve in the future.)
if settings['update']:
    askquestions = False
    # override config settings...
    sys.path.append(configdir)
    from deconv_config_update import deckeyfilenums, deckeynormuseds, \
                                     deckeys, decdirs, decskiplists, decname,\
                                     deckeypsfuseds, decobjname, \
                                     decnormfieldname, decpsfnames
else:
    from config import deckeyfilenums, deckeynormuseds, deckeys, decdirs, \
                       decskiplists, deckeypsfuseds



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

