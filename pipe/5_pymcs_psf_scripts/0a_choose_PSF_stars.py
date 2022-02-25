#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 12:09:41 2021

@author: fred dux






RUNNING THIS SCRIPT IS NOT NECESSARILY NEEDED

Most likely, you will want to take 6 stable stars from your normstars.cat file, 
and put them in the "psfstars.cat" catalogue. 

Then you can skip this file, as all it does it provide an easy way of 
building a psfstars.cat if for some obscure reason none of your normstars can
be a PSF model.

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

from config import configdir
from modules import pickstars

psfcat = os.path.join(configdir, 'psfstars.cat')


pickstars.main(psfcat)