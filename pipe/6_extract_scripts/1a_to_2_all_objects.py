# -*- coding: utf-8 -*-
"""
This script extracts stamps around each object, replaces their NaN and
masks their cosmisc.
"each object" is defined in settings.py ("objkeys")
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
from config import settings, \
                   objkeys, objdirs, objkeyflags, objcosmicskeys, objcoordcats
from modules.variousfct import proquest, mterror, readmancat

# we need to import the functions of the other scripts in this directories.
# unfortunately they start with numbers ...but there is a library for this!
import importlib
extractObj = importlib.import_module('1a_extract_obj')
replaceNaN = importlib.import_module('1b_replacenan_NU')
maskCosmics = importlib.import_module('2_findcosmics_NU')

askquestions = settings['askquestions']

print("I will extract, replace NaN,",
      "and mask cosmics for the following objects:")
for objkey, objdir, objkeyflag, objcosmicskey, objcoordcat in \
             zip(objkeys, objdirs, objkeyflags, objcosmicskeys, objcoordcats):
    print("objkey =", objkey)
    # read the position of the object to extract
    objcoords = readmancat(objcoordcat)
    if len(objcoords) != 1 : 
        raise mterror("Oh boy ... one extraction at a time please !")
    # We do not care about the name that you gave to this source...
    # In fact we do not care about the source at all, 
    # just want to know what part of the image to extract.
    objcoordtxt = "%7.2f %7.2f\n" % (objcoords[0]['x'], objcoords[0]['y'])
    print("Source name = ", objcoords[0]['name'])
    print("coords = ", objcoordtxt)
    

print("Warning, no further questions will be asked beyond this one")
proquest(askquestions)
print("This might take some time...")


for objkey, objdir, objkeyflag, objcosmicskey, objcoordcat in \
             zip(objkeys, objdirs, objkeyflags, objcosmicskeys, objcoordcats):
                 
    extractObj.extractObj(objkey, objcoordcat, objdir, 
                          objkeyflag, objcosmicskey)
    replaceNaN.replaceNaN(objkey, objkeyflag, objdir)
    maskCosmics.maskCosmics(objkey, objkeyflag, objdir)
    
