#!/usr/bin/env python3
# -*- coding: utf-8 -*-
  
#
#	We read your normstars.cat, and draw circles on a png 
#   of your reference images.
#	This will be handy for many tasks.
#	Plus it's nice to get a feeling about your sextractor settings ...
#	

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import alidir, imgdb, settings, normstarscat
from modules.kirbybase import KirbyBase
from modules.variousfct import proquest
from modules import star, f2n


workdir = settings['workdir']
askquestions = settings['askquestions']
identtolerance = settings['identtolerance']
lensregion = settings['lensregion']
emptyregion = settings['emptyregion']


# Read reference image info from database
db = KirbyBase()

refimgname_per_band = settings['refimgname_per_band']
bandswithref = set(refimgname_per_band.values())
for refimgnameband in bandswithref:
    print("You have chosen %s as reference." % refimgnameband)
    refimage = db.select(imgdb, ['imgname'], [refimgnameband], returnType='dict')
    if len(refimage) != 1:
    	print("Reference image identification problem !")
    	sys.exit()
    refimage = refimage[0]
    
    # We put an alias to the reference image into the workdir (for humans only) :
    
    refimgpath = os.path.join(alidir, refimage["imgname"] + "_ali.fits")
    linkpath = os.path.join(workdir, f"{refimage['setname']}_ref.fits")
    if os.path.exists(linkpath) or os.path.islink(linkpath):
    	print("Removing link...")
    	os.remove(linkpath)
    os.symlink(refimgpath, linkpath)
    
    print("I made an alias to this reference image here :")
    print(linkpath)
    
    saturlevel = refimage["saturlevel"] * refimage["gain"]
    print(f"Saturation level (in e-) of ref image : {saturlevel:.2f}")
    
    
    
    # Load the reference sextractor catalog
    refsexcat = os.path.join(alidir, refimage['imgname'] + ".alicat")
    refautostars = star.readsexcat(refsexcat, maxflag = 16, posflux = True)
    refautostars = star.sortstarlistbyflux(refautostars)
    refscalingfactor = refimage['scalingfactor']
    
    # read and identify the manual reference catalog
    refmanstars = star.readmancat(normstarscat) # So these are the "manual" star coordinates
    id = star.listidentify(refmanstars, refautostars, 
                           tolerance=identtolerance, 
                           onlysingle=True, 
                           verbose=True) 
    # We find the corresponding precise sextractor coordinates
    
    
    if len (id["nomatchnames"]) != 0:
    	print("Warning : the following stars could not be identified in the sextractor catalog :")
    	print("\n".join(id["nomatchnames"]))

    	
    preciserefmanstars = star.sortstarlistbyflux(id["match"])
    maxalistars = len(refmanstars)
    
    
    print("I will now generate a png map.")
    proquest(askquestions)
    
    # We convert the star objects into dictionnaries, to plot them using f2n.py
    # (f2n.py does not use these "star" objects...)
    refmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refmanstars]
    preciserefmanstarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in preciserefmanstars]
    refautostarsasdicts = [{"name":s.name, "x":s.x, "y":s.y} for s in refautostars]
    
    
    notfound = [e for e in refmanstarsasdicts if not e['name']\
                                      in [s.name for s in preciserefmanstars]]
    
    
    reffitsfile = os.path.join(alidir, refimage['imgname'] + "_ali.fits")
    
    f2nimg = f2n.fromfits(reffitsfile)
    f2nimg.setzscale(z1=0, z2=1000)
    #f2nimg.rebin(2)
    f2nimg.makepilimage(scale = "log", negative = False)
    
    
    f2nimg.drawstarlist(refautostarsasdicts, r = 30, colour = (150, 150, 150))
    #f2nimg.drawstarlist(refmanstarsasdicts, r = 25, colour = (0, 0, 255))
    f2nimg.drawstarlist(preciserefmanstarsasdicts, r = 5, colour = (255, 0, 0))
    f2nimg.drawstarlist(notfound, r = 9, colour = (255, 255, 0))
    
    
    f2nimg.writeinfo(["Sextractor stars (flag-filtered) : %i" % len(refautostarsasdicts)], 
                     colour = (150, 150, 150))
    f2nimg.writeinfo(["","Identified alignment stars with corrected sextractor coordinates : %i" % len(preciserefmanstarsasdicts)], 
                     colour = (255, 0, 0))

    
    
    # We draw the rectangles around qso and empty region :
    
    lims = [list(map(int,x.split(':'))) for x in lensregion[1:-1].split(',')]
    f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], 
                         colour=(0,255,0), 
                         label = "Lens")
    
    lims = [list(map(int,x.split(':'))) for x in emptyregion[1:-1].split(',')]
    f2nimg.drawrectangle(lims[0][0], lims[0][1], lims[1][0], lims[1][1], 
                         colour=(0,255,0), 
                         label = "Empty")
    
    
    f2nimg.writetitle("Ref : " + refimage['imgname'])
    
    pngpath = os.path.join(workdir, f"{refimage['setname']}_refimg_normstars.png")
    f2nimg.tonet(pngpath)
    
    print("I have written a map into")
    print(pngpath)