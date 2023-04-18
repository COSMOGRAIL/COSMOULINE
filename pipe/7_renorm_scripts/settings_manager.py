#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 14:10:41 2022

@author: fred
"""


import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')



def importSettings(decobjname):
    """
    returns all the deconvolution keys given an object name
    """
    
    from config import settings, configdir
    workdir = settings['workdir']
    decname = settings['decname']
    decnormfieldname = settings['decnormfieldname']
    decpsfnames = settings['decpsfnames']
    setnames = settings['setnames']
    

    decskiplists, deckeyfilenums, deckeypsfuseds  = [], [], []
    deckeynormuseds, decdirs, deckeys, decfiles = [], [], [], []
    for setname in setnames:
        # here we rebuild all the keys that track our deconvolution.
        # (this is normally done in config.py)
        deckey  = f"dec_{setname}_{decname}_{decobjname}_"
        deckey += f"{decnormfieldname}_" + "_".join(decpsfnames)
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
        decfile = os.path.join(decdir, 'stamps-noisemaps-psfs.h5')
        decfiles.append(decfile)


    
    return deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decfiles, decskiplists, deckeypsfuseds, decfiles
