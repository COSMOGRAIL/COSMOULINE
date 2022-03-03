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
from config import imgdb, settings, computer, deconvexe
from modules.variousfct import proquest, notify, nicetimediff
from modules.kirbybase import KirbyBase
from settings_manager import importSettings

db = KirbyBase(imgdb)

askquestions = settings['askquestions']
workdir = settings['workdir']
setnames = settings['setnames']


# import the right deconvolution identifiers:
scenario = "normal"
if len(sys.argv)==2:
    scenario = "allstars"
if settings['update']:
    scenario = "update"
    askquestions = False
    
deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decskiplists, deckeypsfuseds, ptsrccats = importSettings(scenario)

# I am adding this switch here, because I heard that mac computers
# really don't like running two instances of MCS at once. 
# so, by default: false.         
RUNINPARALLEL = False
if computer == "fred":
    RUNINPARALLEL = True

def doOneDeconvolution(deckey, deckeyfilenum, setname, decdir):
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


starttime = datetime.now()
if RUNINPARALLEL:
    from multiprocessing import Pool 
    paramsets = zip(deckeys, deckeyfilenums, setnames, decdirs)
    pool = Pool(4)
    pool.starmap(doOneDeconvolution, paramsets)
else:
    for deckey, deckeyfilenum, setname, decdir in \
                zip(deckeys, deckeyfilenums, setnames, decdirs):
        doOneDeconvolution(deckey, deckeyfilenum, setname, decdir)

