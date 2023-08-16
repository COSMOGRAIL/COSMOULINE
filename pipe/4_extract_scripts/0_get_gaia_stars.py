# -*- coding: utf-8 -*-
"""
Here you will need to inspect your lens position (taken from your settings.py),
and adjust the gaia filtering to select a decent amount of stars close
to our lens. (not too bright, not too faint, not too far ...)

Created on Wed Aug 16 17:38:47 2023

@author: fred
"""
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')
import string
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
from astropy.visualization import AsinhStretch, PercentileInterval
from astropy.visualization.mpl_normalize import ImageNormalize
import matplotlib.pyplot as plt

from config import alidir, imgdb, settings, filtered_gaia_filename, \
                   all_gaia_filename
from modules.kirbybase import KirbyBase






def find_gaia_stars_around_coords(ra, dec, width, height, release='dr3'):
    """

    :param ra:  float, degrees
    :param dec:  float, degrees
    :param radiusarcsec:  float, arcseconds
    :param release: str, default 'dr3'. Either 'dr3' or 'dr2'
    """

    assert release.lower() in ['dr2', 'dr3']
    Gaia.MAIN_GAIA_TABLE = f"gaia{release.lower()}.gaia_source"

    coord = SkyCoord(ra=ra, dec=dec,
                     unit=(u.degree, u.degree),
                     frame='icrs')
    width = width * u.deg
    height = height * u.deg
    r = Gaia.query_object_async(coordinate=coord, 
                                width=width, 
                                height=height)

    return r


db = KirbyBase(imgdb)


_, ramin, ramax, decmin, decmax = db.select(imgdb,  
                                            tablename='common_wcs', 
                                            fields=['ra_min', 'ra_max', 
                                                    'dec_min', 'dec_max'], 
                                            searchData=['*', '*', '*', '*'])[0]

rac = (ramin+ramax)/2
width = abs(ramax-ramin)

decc = (decmin+decmax)/2
height = abs(decmax-decmin)


if not os.path.exists(all_gaia_filename):
    possibilities = find_gaia_stars_around_coords(rac, decc, width, height)
    possibilities.write(all_gaia_filename, format='ascii.csv', overwrite=True)
else:
    possibilities = Table.read(all_gaia_filename)

BRIGHTNESS_THRESHOLD = 16.1
gaia_data = possibilities[possibilities['phot_g_mean_mag']>BRIGHTNESS_THRESHOLD]

# eliminate detections super close to our lens (probably our lens ...)
gaia_coords = SkyCoord(ra=gaia_data['ra'], dec=gaia_data['dec'],
                       unit=(u.deg, u.deg))
lens_coord = SkyCoord(ra=settings['lensRA'], 
                      dec=settings['lensDEC'], 
                      unit=(u.hourangle, u.deg))
distances_to_lens = lens_coord.separation(gaia_coords)
gaia_data['dist'] = distances_to_lens.to('arcsec').value

mask = distances_to_lens > 3*u.arcsec
filtered_gaia_data = gaia_data[mask]
lens_detections = gaia_data[~mask]
# Sort the filtered data by distance
sorted_gaia_data = filtered_gaia_data[distances_to_lens[mask].argsort()]



# here we attempt to filter out the very variable stars by
# thresholding the photometric errors (large if variable over different
# gaia epochs.)
threshold = 3.
threshold2 = 2.
low_variability_sources = sorted_gaia_data[(sorted_gaia_data['phot_g_mean_flux_error'] < threshold) &
                                           (sorted_gaia_data['phot_bp_rp_excess_factor'] < threshold2)]


low_variability_sources = low_variability_sources[:26]
# for historical reasons
# we do not store more than 26 stars. The 26 closest ones.
# because we label normalizations, psfs, etc. with letters.


# so now, index column using the lowercase alphabet
index_values = [string.ascii_lowercase[i] for i in range(len(low_variability_sources))]

# Add the index column to the sorted Gaia data
low_variability_sources['name'] = index_values

low_variability_sources.write(filtered_gaia_filename, format='ascii.csv',
                              overwrite=True)
# load the reference image
refimage = db.select(imgdb, ['imgname'], [settings['refimgname']], 
                     returnType='dict')
if len(refimage) != 1:
    print("Reference image identification problem !")
    sys.exit()
refimage = refimage[0]

refimagepath = os.path.join(alidir, refimage['imgname'] + "_skysub.fits")
with fits.open(refimagepath) as hdul:
    image_data = hdul[0].data
    wcs = WCS(hdul[0].header)

stretch = AsinhStretch(a=0.5)
interval = PercentileInterval(99.9) # Adjust as needed
norm = ImageNormalize(vmin=interval.get_limits(image_data)[0],
                      vmax=interval.get_limits(image_data)[1],
                      stretch=stretch, clip=False)

# convert Gaia coordinates to pixel coordinates
gaia_pixel_coords = wcs.all_world2pix(low_variability_sources['ra'], 
                                      low_variability_sources['dec'], 0)

# get the lens coords as well
lens_pixel_coords = wcs.all_world2pix(lens_coord.ra.deg, lens_coord.dec.deg, 0)
#%%
# Plot the image
plt.figure(figsize=(15, 15))
plt.subplot(projection=wcs)
plt.imshow(image_data, cmap='gray', norm=norm)
# Plot the Gaia stars and add the labels
for coord, label in zip(np.array(gaia_pixel_coords).transpose(), low_variability_sources['name']):
    plt.scatter(coord[0], coord[1], marker='o', edgecolor='r', facecolor='none')
    plt.text(coord[0], coord[1]+10, label, color='red', fontsize=10)

square_size = 30  
plt.plot([lens_pixel_coords[0] - square_size/2, lens_pixel_coords[0] + square_size/2,
          lens_pixel_coords[0] + square_size/2, lens_pixel_coords[0] - square_size/2, lens_pixel_coords[0] - square_size/2],
         [lens_pixel_coords[1] - square_size/2, lens_pixel_coords[1] - square_size/2,
          lens_pixel_coords[1] + square_size/2, lens_pixel_coords[1] + square_size/2, lens_pixel_coords[1] - square_size/2],
         color='blue')
plt.xlabel('RA')
plt.ylabel('Dec')
plt.title('Ref image with chosen Gaia Star Positions')
plt.tight_layout()
plt.savefig(os.path.join(settings['workdir'], 'ref_img_with_gaia_stars.jpeg'), dpi=400)
