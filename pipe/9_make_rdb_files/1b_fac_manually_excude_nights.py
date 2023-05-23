#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 14:15:08 2022

@author: fred
"""

import pycs3
import pycs3.gen
import pycs3.gen.lc_func
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt 
import numpy as np 
from shutil import move, copy

if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import settings, configdir

configdir = Path(configdir)
##############################################################################
##############################################################################
##############################################################################
# import the data - execute the script once for each dataset separately. 
fullname       = settings['lensName']
telescopename  = settings['telescopename']
# names of the curves to be imported from the rdb file:
lcsnames       = settings['sourcenames']
# Shift the lcs in mag for display purposes:
# paths to your data directory and rdb file:
rdbfile        = configdir / (settings['outputname'] + '.rdb')
rdbfilenotcurrated = Path(str(rdbfile).replace('.rdb', '_not_manually_currated.rdb'))
##############################################################################
##############################################################################
##############################################################################

### move the original rdb file to a backup "not manually currated":
if not rdbfilenotcurrated.exists():
    copy(rdbfile, rdbfilenotcurrated)
# we now read from this "not currated" file:
rdbfilenew = rdbfile
rdbfile = rdbfilenotcurrated


# file where we reject our nights:
rejectlist = configdir / "manually_rejected_mjd.txt"



def makeEmptyRejectList(path):
    if not rejectlist.exists():
        with open(path, 'w') as f:
            f.writelines(["#### write here (one by line) mjds you do not wish to include"])
        print(f"I created the reject list at {path}.")
        print("Look at the plot and put the mjds of the nights that seem off there.")
        print("Then, run this again to see an updated plot.")
            
def readRejected(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if not line.startswith('#')]
    mjd = [int(line) for line in lines if line]

    return mjd

rejected = readRejected(rejectlist)

makeEmptyRejectList(rejectlist)



#################### plot of the curves, cross on the manually rejected points
plt.figure(figsize=(17,10))
# read each light curve. 
lcs = []
for lc in lcsnames:
    curve = pycs3.gen.lc_func.rdbimport(rdbfile, f'{lc}', f'mag_{lc}', 
                                        f'magerr_{lc}_5', telescopename)
    mjds = [int(mjd) for mjd in curve.getjds()]
    name = curve.object 
    mags = curve.mags 
    dmags = curve.magerrs 
    plt.errorbar(mjds, mags, yerr=dmags, label=name, marker='o', ls='', ms=4) 
    rejmjd, rejmag = [], []
    # we create and destroy this `rejectedindexes` list as many times
    # as there are curves to plot, but doesn't matter. 
    rejectedindexes = []
    for i, (mjd, mag) in enumerate(zip(mjds, mags)):
        if mjd in rejected:
            rejmjd.append(mjd)
            rejmag.append(mag)
            
            rejectedindexes.append(i)
    plt.plot(rejmjd, rejmag, 'x', color='gray', ms=20, zorder=1000)
    lcs.append(curve)
plt.legend()

plt.show()





# now we need to read the original rdbfile, and re-write it without the rejected
# nights.

with open(rdbfilenotcurrated, "r") as f:
    lines = f.readlines()
headers = lines[:2]
datas = lines[2:]
newdatas = []
for i, data in enumerate(datas):
    if not i in rejectedindexes:
        newdatas.append(data)
        
with open(rdbfilenew, "w") as f:
    f.writelines(headers + newdatas)
