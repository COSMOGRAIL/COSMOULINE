#	
#	Do the deconvolution
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

askquestions = settings['askquestions']
workdir = settings['workdir']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']
decpsfnames = settings['decpsfnames']
decobjname = settings['decobjname']
refimgname = settings['refimgname']


# this script can be ran with an object to deconvolve as an argument.
# in this case, force the rebuild of all the keys
if len(sys.argv) == 2:
    decobjname = sys.argv[1]
    deckey  = f"dec_{decname}_{decobjname}_{decnormfieldname}_"
    deckey += "_".join(decpsfnames)
    ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
    decskiplist = os.path.join(configdir,deckey + "_skiplist.txt")
    deckeyfilenum = "decfilenum_" + deckey
    deckeynormused = "decnorm_" + deckey
    decdir = os.path.join(workdir, deckey)
    print("You are running the deconvolution on all the stars at once.")
    print("Current star : " + sys.argv[1])


# moreover, if this is an udpate: read the config file produced by the
# original deconvolution.
if settings['update']:
    askquestions = False
    # override config settings...
    sys.path.append(configdir)
    from deconv_config_update import deckeyfilenum, deckey, decdir
else:
    from config import deckeyfilenum, deckey, decdir
print(f"Starting deconvolution {deckey}")

db = KirbyBase()
images = db.select(imgdb, [deckeyfilenum], 
                          ['\d\d*'], 
                          returnType='dict', useRegExp=True, 
                          sortFields=[deckeyfilenum])
nbimg = len(images) + 1
print(f"{nbimg} images (ref image is duplicated)")

proquest(askquestions)

print("Of course I do not update the database here,")
print("so you can go on with something else in the meantime.")


starttime = datetime.now()
db = KirbyBase()
# WARNING the sorting below is important !!!!!!!
images = db.select(imgdb, [deckeyfilenum], 
                          ['\d\d*'], 
                          returnType='dict', useRegExp=True, 
                          sortFields=[deckeyfilenum]) 

origdir = os.getcwd()

os.chdir(decdir)
os.system(deconvexe)
os.chdir(origdir)

endtime = datetime.now()
timetaken = nicetimediff(endtime - starttime)

notify(computer, settings['withsound'], 
       f"I've deconvolved {deckey} in {timetaken} .")


