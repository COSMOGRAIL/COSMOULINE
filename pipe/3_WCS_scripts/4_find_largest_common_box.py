from astropy.wcs import WCS
from astropy.io import fits
import sys
import os

# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))
# if ran interactively, append the parent manually as sys.path[0] 
# will be emtpy.
sys.path.append('..')

from config import alidir, imgdb, settings
from modules.kirbybase import KirbyBase

from pathlib import Path
alidir = Path(alidir)

db = KirbyBase(imgdb)
if settings['thisisatest']:
    print("This is a test.")
    images = db.select(imgdb, ['gogogo','treatme', 'testlist'],
                              [ True,    True,      True],
                              ['recno','imgname'],
                              sortFields=['imgname'],
                              returnType='dict')
elif settings['update']:
    print("This is an update.")
    images = db.select(imgdb, ['gogogo','treatme', 'updating'],
                              [ True,    True,      True],
                              ['recno','imgname'],
                              sortFields=['imgname'],
                              returnType='dict')
else:
    images = db.select(imgdb, ['gogogo','treatme'],
                              [ True,    True],
                              ['recno','imgname'],
                              sortFields=['imgname'],
                              returnType='dict')

fits_files = [alidir / f"{im['imgname']}_skysub.fits" for im in images]

# Lists to hold the boundaries
ra_mins, ra_maxs, dec_mins, dec_maxs = [], [], [], []

# Loop through the FITS files
for file in fits_files:
    with fits.open(file) as hdul:
        wcs = WCS(hdul[0].header)
        # Get the image shape
        shape = hdul[0].data.shape
        # Convert pixel coordinates of the boundaries to world coordinates
        ra_min, dec_min = wcs.all_pix2world(0, 0, 0)
        ra_max, dec_max = wcs.all_pix2world(shape[1]-1, shape[0]-1, 0)
        ra_mins.append(ra_min)
        ra_maxs.append(ra_max)
        dec_mins.append(dec_min)
        dec_maxs.append(dec_max)

# Find the intersection of all boundaries
ra_min_common = min(ra_mins)
ra_max_common = max(ra_maxs)
dec_min_common = max(dec_mins)
dec_max_common = min(dec_maxs)

# The largest common box
common_box = (ra_min_common, ra_max_common, dec_min_common, dec_max_common)
print("adding this box to DB:", common_box)
fields = ['ra_min:float', 'ra_max:float', 
          'dec_min:float', 'dec_max:float']


db.execute(imgdb, 'DROP TABLE IF EXISTS common_wcs')

db.create(imgdb, fields=fields,
                 tablename="common_wcs")

db.insert(imgdb, tablename='common_wcs',
                 dic={
                         'ra_min':  ra_min_common,
                         'ra_max': ra_max_common,
                         'dec_min': dec_min_common,
                         'dec_max': dec_max_common
                     })
