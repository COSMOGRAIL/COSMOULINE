#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 12:09:41 2021

@author: fred
"""

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

import pickstars

pickstars.main(normstarscat)
