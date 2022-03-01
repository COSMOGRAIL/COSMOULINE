#    
#    Do the deconvolution
#
from datetime import datetime
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, configdir, computer, deconvexe
from modules.variousfct import proquest, notify, nicetimediff
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
    deckeynormuseds, decdirs, deckeys, ptsrccats = [], [], [], []
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
        ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
        ptsrccats.append(ptsrccat)

# moreover, if this is an udpate: read the config file produced by the
# original deconvolution.
if settings['update']:
    askquestions = False
    # override config settings...
    sys.path.append(configdir)
    from deconv_config_update import deckeyfilenums, deckeys, decdirs
else:
    from config import deckeyfilenums, deckeys, decdirs, ptsrccats
    
    
starttime = datetime.now()
for deckey, deckeyfilenum, setname, decdir in \
            zip(deckeys, deckeyfilenums, setnames, decdirs):
    print(f"deckey : {deckey}") 
    print(f"Starting deconvolution {deckey}")
    
    
    images = db.select(imgdb, [deckeyfilenum], 
                              ['\d\d*'], 
                              returnType='dict', useRegExp=True, 
                              sortFields=[deckeyfilenum])
    nbimg = len(images) + 1
    print(f"{nbimg} images (ref image is duplicated)")
    
    proquest(askquestions)
    
    print("Of course I do not update the database here,")
    print("so you can go on with something else in the meantime.")


    origdir = os.getcwd()
    
    os.chdir(decdir)
    os.system(deconvexe)
    os.chdir(origdir)
    
    endtime = datetime.now()
    timetaken = nicetimediff(endtime - starttime)
    
    notify(computer, settings['withsound'], 
           f"I've deconvolved {deckey} in {timetaken} .")


