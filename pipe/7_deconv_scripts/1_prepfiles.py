#    
#    Here we are. Finally.
#    The first main task of this script is to "put together" 
#    the right psfs for each image,
#    and complain if, for instance, one image has no psf, etc.
#    We have to look at the PSF rejection lists, as well as at the decskiplist.
#    We will do all this in memory, before touching 
#    to the database or starting anything.
#
#    Then :
#    copy the right stuff to the decdir, 
#    with the right filenames (0001, 0002, ...)
#    for identification, the "file-numbers" will be written 
#    into the db (as well as the psfname and norm coeff to use)
#
#    reference image will be put at first place, i.e. 0001
#
"""
MULTI-SETNAME UPDATE

We are making the deckey more verbose by adding the setname as well.
(the other keys built on deckey are also naturally also changed)
Then, we prepare one deconvolution per setname: this allows for the
simultaneous treatment of different bands.


THIS HAS CONSEQUENCES FOR UPDATES
the following keys, given in deconv_config_update.py (in your config dir):
    decskiplist, deckeyfilenum, deckeypsfused,
    deckeynormused, decdir, deckey
become
    decskiplists, deckeyfilenums, deckeypsfuseds,
    deckeynormuseds, decdirs, deckeys

To use an old deconv_config_update.py: rename the said variables,
and add brakets [ ] around their assigned value to make them lists. 
"""

import shutil
import sys
import os
import h5py
import numpy as np
from pathlib import Path
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import dbbudir, imgdb, settings, configdir, computer, psfdir,\
                   psfsfile, extracteddir
from modules.variousfct import proquest, readimagelist, mterror, mcsname,\
                               backupfile, notify
from modules.kirbybase import KirbyBase
from settings_manager import importSettings

db = KirbyBase(imgdb)  

askquestions = settings['askquestions']
workdir = settings['workdir']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']
decpsfnames = settings['decpsfnames']
decobjname = settings['decobjname']
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

# an awful for loop on all the bands:
# this will prepare one deconvolution per setname. 
# (e.g. a deconvolution directory, a key that identifies it for the database,
# and all that stuff.)
for deckey, decskiplist, deckeyfilenum, setname, \
        deckeypsfused, deckeynormused, decdir in \
    zip(deckeys, decskiplists, deckeyfilenums, setnames, \
        deckeypsfuseds, deckeynormuseds, decdirs):
        
    # we're working in some band/setname now. the ref img of this particular
    # band is:
    refimgname = refimgname_per_band[setname]
        
    # Some first output for the user to check :
    print(f"Name for this deconvolution : {decname}.")
    if settings['thisisatest'] :
        print("This is a test run.")
    else :
        print("This is NOT a test run !")
    print(f"You want to deconvolve the object '{decobjname}'",
          " with the PSFs from :")
    for psfname in decpsfnames:
        print(psfname)
    print("And you want to normalize using :", decnormfieldname)
    
    proquest(askquestions)
    
    # And a check of the status of the decskiplist :
    
    if os.path.isfile(decskiplist):
        print("The decskiplist already exists :")
    else:
        cmd = "touch " + decskiplist
        os.system(cmd)
        print("I have just touched the decskiplist for you :")
    print(decskiplist)
    
    # image[1] would be the comment:
    decskipimages = [image[0] for image in readimagelist(decskiplist)] 
    print(f"It contains {len(decskipimages)} images.")
    
    #proquest(askquestions)
    
    
    # We have a look at the psfkicklists and the flags 
    # for each psf in the database:
    print("Ok, now looking at the PSFs ...")
    
    # we will build a dictionary, one entry for each psfname, containing
    # available images.
    psfimages = {}    
    
    for particularpsfname in decpsfnames:
        print("- " * 30)
        # the database
        particularpsfkey = "psf_" + particularpsfname
        particularpsfkeyflag = "flag_" + particularpsfkey
        # we get a list of imgnames:
        particulartreatedimages = db.select(imgdb, [particularpsfkeyflag], 
                                                   [True], ['imgname'])
        # the [0] is just to get rid of the list-of-list structure:
        particulartreatedimages = [image[0] 
                                   for image in particulartreatedimages] 
        
        
        # the skiplist
        particularskiplist = os.path.join(configdir, 
                                          f"{particularpsfkey}_skiplist.txt")
        # image[1] would be the comment:
        particularskiplistimages = [image[0] 
                        for image in readimagelist(particularskiplist)] 
        
        print(f"{particularpsfname:15}: {len(particulartreatedimages):4},",
              f"but {len(particularskiplistimages):3} on skiplist.")
        
        # ok, now we combine the two lists :
        
        particulartreatedimages = set(particulartreatedimages)
        particularskiplistimages = set(particularskiplistimages)
        if not particularskiplistimages.issubset(particulartreatedimages):
            errors = particularskiplistimages.difference(particulartreatedimages)
            print("WARNING : the following skiplist items are not part",
                  "of that PSF set!")
            print("They might be typos...")
            for error in errors:
                print(error)
                
        particularavailableimages = \
                    particulartreatedimages.difference(particularskiplistimages)
                       
        print("Number of available psfs :", len(particularavailableimages))
        # here we add those to the dict.:
        psfimages[particularpsfname] = list(particularavailableimages) 
    
    print("- " * 30)
    
    # Now we should be able to attribute one precise psf 
    # for every image to deconvolve.
    # we start by selecting the images we want to use 
    # (treatme and or testlist, as usual)
    # before this you could perhaps put treatme (or gogogo ?)
    # to false for bad seeing etc...
    
    if settings['thisisatest'] :
        print("This is a test run.")
        images = db.select(imgdb, ['gogogo', 'treatme', 'testlist', 'setname'], 
                                  [True, True, True, setname], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
        refimage = [image for image in images if image['imgname'] == refimgname][0]
    else :
        images = db.select(imgdb, ['gogogo', 'treatme', 'setname'], 
                                  [True, True, setname], 
                                  returnType='dict', 
                                  sortFields=['setname', 'mjd'])
        refimage = [image for image in images if image['imgname'] == refimgname][0]
    
    
    print("Number of images selected from database",
          "(before psf attribution or decskiplist):", 
          len(images))
    
    # images is now a list of dicts. 
    # We will write the psf to use into this dict.
    
    for image in images:
        image['choosenpsf'] = "No psf"
        for psfname in decpsfnames:
            if image['imgname'] in psfimages[psfname]:
                image['choosenpsf'] = psfname
        # this means that the last psf available 
        # from the decpsfnames will be used.
    
    
    nopsfimages = [image['imgname'] for image in images 
                         if image['choosenpsf'] == "No psf"]
    if len(nopsfimages) > 0:
        print(f"WARNING : I found {len(nopsfimages)}",
              "images without available psf :")
        for imagename in nopsfimages:
            print(imagename)
        print("I will thus not use them in the deconvolution !")
    
    havepsfimages = [image for image in images 
                        if image['choosenpsf'] != "No psf"]
    print("Number of images that have a valid PSF",
          "(again, before looking at decskiplist) :", 
          len(havepsfimages))
    
    # we do now a check for the object extraction
    # Missing objects are not tolerated. We would simply stop.
    
    print("Now looking for the object itself ...")
    
    objkey = "obj_" + decobjname
    objkeyflag = "flag_" + objkey
    
    if objkeyflag not in db.getFieldNames(imgdb):
        raise mterror(f"Your object {decobjname} is not yet extracted !")
    noobjimages = [image['imgname'] for image in images 
                              if image[objkeyflag] != True]
    if len(noobjimages) > 0:
        raise mterror(f"{len(noobjimages)} images have no objects extracted !")
    
    objimages = [image['imgname'] for image in images 
                              if image[objkeyflag] == True] 
    print("I've found", len(objimages), "extracted objects.")
    # (In fact this is trivial, will not be used later.)
    
    # havepsfimages are for now the ones to go.
    # It's time to look at the decskipimages.
    
    print("Images that have a valid PSF :", len(havepsfimages))
    print("Images on your decskiplist :", len(decskipimages))
    # (note that this list contains only the names!)
    readyimages = [image for image in havepsfimages 
                       if image["imgname"] not in decskipimages]
    print("Images with valid PSF not on decskiplist :", len(readyimages))
    print("(i.e. I will prepare the deconvolution for this last category !)")
    
    if len(readyimages) >= 2500:
        print("This is too much, MCS in fortran can only",
              "handle less than 2500 images.")
        sys.exit()
    
    # But while we are at it let's check if there are any "typos" 
    # in the decskiplist :
    alls = db.select(imgdb, ['recno'], ['*'], ["imgname"])
    possibleimagenameset = set([imgnamelist[0] for imgnamelist in alls])
    decskipimagenameset = set(decskipimages)
    
    if not decskipimagenameset.issubset(possibleimagenameset):
        errors = decskipimagenameset.difference(possibleimagenameset)
        print("WARNING : I can't find the following decskiplist", 
              "items in the database !")
        for error in errors:
            print(error)
        raise mterror("Fix this (see above output).")
    
    #proquest(askquestions)
    
    
    # a check about the reference image:
    if refimgname not in [image['imgname'] for image in readyimages] :
        print("The reference image is not in your initial selection!")
        print("Do you want me to add it ? Or do you prefer for me to crash?")
        proquest(askquestions)
        readyimages.append(refimage)
    if refimgname in nopsfimages :
        raise mterror("No PSF available for reference image !")
    
    
    # we check if this deconvolution was already done before :
    
    if os.path.isdir(decdir):
        print("I will delete the existing deconvolution.")
        proquest(askquestions)
        shutil.rmtree(decdir)
        print("It's too late to cry now.")
        os.mkdir(decdir)
    else :
        os.mkdir(decdir)
    
    # everything seems fine for the input so let's go
    
    # this is a code that will idendtify this particular deconvolution:
    print("I will now prepare the database. deckey :", deckey) 
    proquest(askquestions)
    backupfile(imgdb, dbbudir, "prepfordec_"+deckey)
    
    
    if deckeyfilenum in db.getFieldNames(imgdb):
        db.dropFields(imgdb, [deckeyfilenum, deckeypsfused, deckeynormused])    
                            # we erase the previous fields for this deckey
                            # this full erase is important, as we will use the 
                            # simple presence of these numbers to identify 
                            # images used in this deconvolution !
        
    db.addFields(imgdb, [f'{deckeyfilenum}:str', 
                         f'{deckeypsfused}:str', 
                         f'{deckeynormused}:float'])
        
    
    
    # Now we have to "copy" the reference image to the first position.
    # But we will leave it inside the normal list, so it will be duplicated.
    
    
    # We select the reference image
    refimage = [image for image in readyimages 
                    if image['imgname'] == refimgname][0]
    # And copy it into the first positon :
    readyimages.insert(0, refimage)
    # readyimages now contains n+1 images !!!!
    
    
    # we'll read the different parts we need for each image in the next
    # loop
    # stamps and noies maps of the object at hand:
    extractedh5 = h5py.File(extracteddir / f'{setname}_extracted.h5', 'r')
    psfsh5 = h5py.File(psfsfile, 'r')
    # psfs in `psfsfile`
    stamplist = []
    noisestamplist = []
    psflist = []
    for i, image in enumerate(readyimages):
        imgname = image['imgname']
        # so we start at i = 1!!!
        # i = 1 is reserved for the copy of the ref image:
        decfilenum = mcsname(i+1); 
        print("- " * 40)
        print(decfilenum, "/", len(readyimages), ":", image['imgname'])
        
        # We know which psf to use :
        print(f"PSF : {image['choosenpsf']}")
        
        # We select the normalization on the fly, 
        # as this is trivial compared to the psf selection :
        if decnormfieldname == "None":
            image["choosennormcoeff"] = 1.0    
            # in this case the user *wants* to make a 
            # deconvolution without normalization.
        else :
            image["choosennormcoeff"] = image[decnormfieldname]
            if image["choosennormcoeff"] == None:
                print("WAAAAARRRRNIIIING: no coeff available, using 1.0!")
                image["choosennormcoeff"] = 1.0
        print(f"Norm. coefficient : {image['choosennormcoeff']:.3f}")
            
        
  
        
        
        normcoeff = image["choosennormcoeff"]
        
        stamp = normcoeff * np.array(extractedh5[f"{decobjname}_{imgname}"])
        stampnoise = normcoeff * np.array(extractedh5[f"{decobjname}_{imgname}_noise"])
        psf = psfsh5[imgname]
        
        stamplist.append(stamp)
        noisestamplist.append(stampnoise)
        psflist.append(psf)
 
    
        # For the duplicated ref image, we do not update the database !
        # As in fact, there is no duplicated ref image in the database...
        if i != 0 : # that is mcsname != 0001
            db.update(imgdb, ['recno'], 
                             [image['recno']], 
                             {deckeyfilenum: decfilenum, 
                              deckeypsfused: image['choosenpsf'], 
                              deckeynormused: image["choosennormcoeff"]})
    
        # numbers in the db start with 0002
    # ok, save the array of stamps
    decfile = Path(decdir) / 'stamps-noisemaps-psfs.h5'
    with h5py.File(decfile, 'w') as f:
        f['stamps'] = np.array(stamplist)
        f['noisemaps'] = np.array(noisestamplist)
        f['psfs'] = np.array(psflist)
    
    # close open files
    extractedh5.close()
    psfsh5.close()
    
    print("- " * 40)
    db.pack(imgdb)
    notify(computer, settings['withsound'], 
           f"Hello again.\nI've prepared {len(readyimages)} images for {deckey}")
    print("(Yes, one more, as I duplicated the ref image.)")
