# This is just a little helper script, not required at all !
# We read in2.txt as resulting from the deconv, and translate it into
import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import settings, imgdb
from modules.variousfct import proquest
from modules.kirbybase import KirbyBase
from modules import star
from settings_manager import importSettings


db = KirbyBase(imgdb)

askquestions = settings['askquestions']
workdir = settings['workdir']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']
decpsfnames = settings['decpsfnames']
decobjname = settings['decobjname']
refimgname = settings['refimgname']
refimgname_per_band = settings['refimgname_per_band']
setnames = settings['setnames']
sample_only = settings['sample_only']
uselinks = settings['uselinks']
makejpgarchives = settings['makejpgarchives']


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

for deckey, decskiplist, deckeyfilenum, setname, ptsrccat, \
        deckeypsfused, deckeynormused, decdir in \
            zip(deckeys, decskiplists, deckeyfilenums, setnames, ptsrccats, \
                deckeypsfuseds, deckeynormuseds, decdirs):
                
    in2filepath = os.path.join(decdir, "in2.txt")
    in2file = open(in2filepath, "r", encoding="ISO-8859-1")
    in2filelines = in2file.readlines()
    in2file.close()
    
    print("Reading from :")
    print(in2filepath)
    
    ptsrcs = star.readmancat(ptsrccat)
    nbptsrcs = len(ptsrcs)
    
    #print in2filelines
    
    # quick and dirty filtering of the trash ...
    goodlines = []
    for line in in2filelines:
        if line[0] == "-" or line[0] == "|":
            continue
        print(line)
        goodlines.append(line)
    
    # we translate all this into a tiny db :
    
    ptsrcdb = []
    for (i, ptsrc) in enumerate(ptsrcs):
        xpos = (float(goodlines[2*i + 1].split()[0])+0.5)/2.0
        ypos = (float(goodlines[2*i + 1].split()[1])+0.5)/2.0
        influx = ptsrc.flux
        # we count the ref image only once here:
        in2flux = float(np.median(list(
            map(float, np.array(goodlines[2*i].split()[1:]))))) 
        ptsrcdb.append({"name":ptsrc.name, "xpos":xpos, "ypos":ypos, 
                        "influx":influx, "in2flux":in2flux})
    
    
    # And we print this out:
    
    print("\nOutput astrometry with input photometry :")
    for ptsrc in ptsrcdb:
        print(f"{ptsrc['name']}\t{ptsrc['xpos']:f}\t")
        print(f"{ptsrc['ypos']:f}\t{ptsrc['influx']:f}\n")
    
    print("\nOutput astrometry and median output photometry :")
    for ptsrc in ptsrcdb:
        print(f"{ptsrc['name']}\t{ptsrc['xpos']:f}\t")
        print(f"{ptsrc['ypos']:f}\t{ptsrc['in2flux']:f}\n")
    
    
    print("\nShould I write the last version to your point star catalog?")
    proquest(askquestions)
    cat = open(ptsrccat,'w')
    for ptsrc in ptsrcdb:
        cat.write(f"\n{ptsrc['name']}\t{ptsrc['xpos']:f}\t")
        cat.write(f"{ptsrc['ypos']:f}\t{ptsrc['in2flux']:f}")
    cat.close()
    print("OK, your point star catalogue is edited !")
