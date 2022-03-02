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



def importSettings(scenario):
    """
    returns the right set of keys depending on how we're running the
    deconvolution scripts. 
    normal: all the keys are read from the config file
    allstars: force the rebuild of the keys, because we're forcing the
              scripts to treat a specific object.
    update: read the keys from a special config file produced in a previous
            deconvolution.
    """
    
    from config import settings, configdir
    workdir = settings['workdir']
    decname = settings['decname']
    decnormfieldname = settings['decnormfieldname']
    decpsfnames = settings['decpsfnames']
    decobjname = settings['decobjname']
    setnames = settings['setnames']
    
    if scenario == "normal":
        from config import deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
                           decskiplists, deckeypsfuseds, ptsrccats
    elif scenario == "allstars":
        # this script can be ran with an object to deconvolve as an argument.
        # in this case, force the rebuild of all the keys
        print("You are running the deconvolution on all the stars at once.")
        print("Current star : " + sys.argv[1])
        decskiplists, deckeyfilenums, deckeypsfuseds  = [], [], []
        deckeynormuseds, decdirs, deckeys, ptsrccats = [], [], [], []
        for setname in setnames:
            # here we rebuild all the keys that track our deconvolution.
            # (this is normally done in config.py)
            decobjname = sys.argv[1]
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
            ptsrccat = os.path.join(configdir, deckey + "_ptsrc.cat")
            ptsrccats.append(ptsrccat)


    # if this is an udpate: read the config file produced by the
    # original deconvolution.
    elif scenario == "update":
        # override config settings...
        sys.path.append(configdir)
        from deconv_config_update import deckeyfilenums, deckeynormuseds, \
                                         deckeys, decdirs, decskiplists, \
                                         deckeypsfuseds, ptsrccats
    else:
        raise AssertionError(f"No settings for scenario {scenario}.")
    
    return deckeyfilenums, deckeynormuseds, deckeys, decdirs,\
           decskiplists, deckeypsfuseds, ptsrccats

