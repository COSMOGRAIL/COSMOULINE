#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOU WILL NEED AN ASTROMETRY.NET API KEY TO RUN THIS.
CREATE AN ACCOUNT THERE, GET THE API KEY, AND PUT IT IN YOUR ENVIRONMENT:
    
    $ export astrometry_net_api_key="....."

Created on Wed Aug 16 00:47:27 2023

@author: fred
"""

from astropy.io import fits
import sys
import os
from astroquery.astrometry_net import AstrometryNet
import requests
import json

sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')

from config import alidir, imgdb, settings
from modules.kirbybase import KirbyBase
from modules import star


askquestions = settings['askquestions']
refimgname = settings['refimgname']
db = KirbyBase(imgdb)


# get the info from the reference frame
refimage = db.select(imgdb, ['imgname'], [refimgname], returnType='dict')
if len(refimage) != 1:
    print("Reference image identification problem !")
    sys.exit()
refimage = refimage[0]

# load the reference sextractor catalog
refsexcat = os.path.join(alidir, refimage['imgname'] + ".cat")
refautostars = star.readsexcat(refsexcat, maxflag=16, posflux=True)
refautostars = star.sortstarlistbyflux(refautostars)
refscalingfactor = refimage['scalingfactor']
# astroalign likes tuples, so let's simplify our star objects to (x,y) tuples:
tupleref = [(s.x, s.y) for s in refautostars]
x, y = list(zip(*tupleref))

# get an astrometry.net session:
R = requests.post('http://nova.astrometry.net/api/login', 
                  data={'request-json': json.dumps({"apikey": os.environ['astrometry_net_api_key']})})

# create an object to interact with our session:
ast = AstrometryNet()
ast._session_id = R.json()['session']

# load our ref image:
fits_file_path = os.path.join(alidir, f"{refimgname}_skysub.fits")
hh = fits.getheader(fits_file_path)
nx, ny = hh['NAXIS1'], hh['NAXIS2']

# aaand get the WCS. If not internet connection .......
# well you can still do it by hand.
wcs = ast.solve_from_source_list(x, y, nx, ny)
# put that into the ref image.
with fits.open(fits_file_path, mode="update") as hdul:
    hdul[0].header.update(wcs)
    hdul.flush()  
