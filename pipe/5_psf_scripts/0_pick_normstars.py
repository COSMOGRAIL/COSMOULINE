#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 12:09:41 2021

@author: fred
"""

import sys
import os
from shutil import copy
from glob import glob
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
    
from config import normstarscat, photomstarscat
from modules import pickstars

pickstars.main(normstarscat, workonali=True)

print(4*"\n", "###############################################################")
print("I will copy these over to your photomstars catalogue as well.")
print("(This is useful in the next steps, and after deconvolving the ")
print(" said photomstars in 7, you will remove those that vary too much ")
print(" from your photomstars catalogue.)")

if os.path.exists(photomstarscat):
    # back up if it already exists. 
    bcpnametemplate = os.path.normpath(photomstarscat)+'*.bcp'
    nbackups = glob(bcpnametemplate)
    N = len(nbackups)+1
    newname =  os.path.normpath(photomstarscat)+f'.{N}.bcp'
    copy(photomstarscat, newname)
    print(f"Old photomstars catalogue backed up to {newname}")
# now that things are backed up, overwrite:
copy(normstarscat, photomstarscat)