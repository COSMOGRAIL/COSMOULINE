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

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

from os.path import join

psfcat = join(configdir, 'psfstars.cat')


import pickstars
pickstars.main(psfcat)