#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:46:31 2023

@author: fred dux


This file 
 - selects all the images matching our settings.py configuration,
 - extracts the wanted regions from them
 - at the same time, builds a noise map for each region of each image
 - helps the user create masks with ds9
 - applies the created masks to our noise maps (sets noise to 1e8 for masked pixels)

"""

import os
import sys
import h5py
from   pathlib    import Path
import numpy      as     np
from   astropy.io import fits
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table

sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')
from config import settings, imgdb, alidir, extracteddir, \
                   filtered_gaia_filename
from modules.kirbybase import KirbyBase


stampsize = settings['stampsize']
alidir = Path(alidir)
extracteddir = Path(extracteddir)

update = settings['update']
askquestions = settings['askquestions']
refimgname = settings['refimgname']

db = KirbyBase(imgdb)

 
gaia_stars = Table.read(filtered_gaia_filename)


def extract_stamp(data, header, ra, dec, cutout_size=6):
    """
    :param data: 2d numpy array containing the full image
    :param header: fits header for WCS info
    :param ra: float, degrees
    :param dec: float, degrees
    :param cutout_size: float, arcseconds
    :return: 2d cutout array, 2d cutout noisemap array, wcs string of cutout
    """

    cutout_size = (cutout_size, cutout_size) * u.arcsec
    coord = SkyCoord(ra*u.deg, dec*u.deg)

    wcs = WCS(header)
    datacutout = Cutout2D(data, coord, cutout_size, wcs=wcs, mode='partial')
    # let's also carry the WCS of the cutouts, will be useful for the intial guess of
    # the positions of the lensed images later.
    wcs_header = datacutout.wcs.to_header()
    wcs_header_string = wcs_header.tostring()
    
    # now just take the numpy array
    datacutout = datacutout.data


    
    # noise map given that the data is in electrons ...
    stddev = 0.25 * (  np.nanstd(datacutout[:, 0]) \
                     + np.nanstd(datacutout[0, :]) \
                     + np.nanstd(datacutout[:, -1]) \
                     + np.nanstd(datacutout[-1, :])
                    )
    nmap = stddev + np.sqrt(np.abs(datacutout))
    # remove zeros if there are any ...
    nmap[nmap < 1e-7] = 1e-7

    return datacutout, nmap, wcs_header_string


# We select the images, according to "thisisatest".
# Note that only this first script of the psf construction looks at this :
# the next ones will simply look for the psfkeyflag in the database !
if settings['thisisatest'] :
    print("This is a test run.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'testlist'], 
                              [True, True, True], returnType='dict')
elif settings['update']:
    print("This is an update.")
    images = db.select(imgdb, ['gogogo', 'treatme', 'updating'], 
                              [True, True, True], returnType='dict')
else :
    images = db.select(imgdb, ['gogogo', 'treatme'], 
                              [True, True], returnType='dict')


print(f"I will treat {len(images)} images.")

# where we'll save our stamps
regionsfile = extracteddir / 'regions.h5'
# start from scratch ...
if regionsfile.exists():
    # delete if exists.
    regionsfile.unlink()


for i,image in enumerate(images):
    print(40*"- ")
    print("%i / %i : %s" % (i+1, len(images), image['imgname']), end= ' ')
    
    image_file = alidir / f"{image['imgname']}_skysub.fits"
    
    # skysub images are in e-
    try:
       data, header = fits.getdata(image_file), fits.getheader(image_file)
    except Exception as E:
       db.update(imgdb, ['recno'], [image['recno']], [False], ['gogogo'])
       print("Eliminated image", image['imgname'], '. Exception:', E)
       continue
    
    with h5py.File(regionsfile, 'a') as regf:
        # organize hdf5 file
        imset = regf.create_group(image['imgname'])
        stampset = imset.create_group('stamps')
        noiseset = imset.create_group('noise')
        wcsset = imset.create_group('wcs')
        # useful when masking cosmics.
        _ = imset.create_group('cosmicsmasks')

        # extract the stars
        for row in gaia_stars:
            ra, dec = row['ra'], row['dec']
            
            reg, nmap, wcsstr = extract_stamp(data, header, ra, dec, stampsize)

            sourceid = str(row['name'])
            stampset[sourceid] = reg
            noiseset[sourceid]= nmap
            wcsset[sourceid] = wcsstr
            
        # aand extract the lens.
        lens_coord = SkyCoord(ra=settings['lensRA'], 
                              dec=settings['lensDEC'], 
                              unit=(u.hourangle, u.deg))
        reg, nmap,  wcsstr = extract_stamp(data, header, 
                                           lens_coord.ra.value,
                                           lens_coord.dec.value,
                                           stampsize)
        stampset['lens'] = reg
        noiseset['lens'] = nmap
        wcsset['lens'] = wcsstr
