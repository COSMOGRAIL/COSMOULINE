#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 18:04:17 2022

@author: fred dux

Here we defringe the images 
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

from config import alidir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules.variousfct import fromfits, proquest, tofits
from modules.poor_mans_defringe import estimateFringes


askquestions = settings['askquestions']
workdir = settings['workdir']


db = KirbyBase()




if settings['thisisatest']:
	print("This is a test run.")
	images = db.select(imgdb, ['gogogo','treatme','testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
	print("This is an update.")
	images = db.select(imgdb, ['gogogo','treatme','updating'], 
                              [True, True, True], returnType='dict')
	askquestions = False
else:
	images = db.select(imgdb, ['gogogo','treatme'], 
                              [True, True], returnType='dict')

    
nbrimages = len(images)
print("Number of images to treat :", nbrimages)
proquest(False)

def doDefringe(image):
    imagepath = os.path.join(alidir, image["imgname"] + "_skysub.fits")
    (fringed, header) = fromfits(imagepath, verbose=False)
    fringes = estimateFringes(imagepath)
    defringed = fringed- fringes 
    defringedpath = os.path.join(alidir, image["imgname"] + "_defringed.fits")
    tofits(defringedpath, defringed, header)

if computer == 'fred':
    from multiprocessing import Pool 
    pool = Pool(6)
    pool.map(doDefringe, images)
else:
    for image in images:
        doDefringe(image)


