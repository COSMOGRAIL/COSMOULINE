"""
Open the headers off all images in folderpath (ECAM prered images), read various
 values that
and save it in a numpy file. To be used in COSMOULINE/9_quicklook/7b and 7c, to 
correlate with 
the ellipticity and position angle.
"""
execfile("../config.py")  # probably not needed...
from kirbybase import KirbyBase, KBError
import numpy as np
import glob, sys, os
import astropy.io.fits as pyfits #use astropy.io.fits if you are not stuck in 2010 anymore

# read the headers of the original data files
vals = []
# we look only at the UL files, simpler
folderpath = rawdir
filepaths = glob.glob(os.path.join(folderpath, "*.fits"))
lens_set = workdir.split('/')[-1]

for i, f in enumerate(filepaths):
	print i+1, "/", len(filepaths)
	header = pyfits.getheader(f)
	vals.append({
	"derot": header["HIERARCH OGE ADA ROTMEASURED"],
	"azi": header["HIERARCH OGE TEL TARG AZI START"],
	"elev": header["HIERARCH OGE TEL TARG ELE START"], 
	"windspeed": header["HIERARCH OGE AMBI WINDSP"],
	"winddir": header["HIERARCH OGE AMBI WINDDIR"],
	"imgname": os.path.basename(f).split(".fits")[0]
	})

np.save(os.path.join(workdir,"valstemp_%s.npy"%lens_set), vals)

# 1620+1203 0158-4325 0832+0404, 1131-123, 2033-4723

