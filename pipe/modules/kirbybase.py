#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 12:20:04 2022
@author: fred
"""

BACKEND = "SQLITE"

if BACKEND == "SQLITE":
    from sqlitebase import KirbyBase, KBError 
else:
    from kirbybase_text import KirbyBase, KBError 
