#!/usr/bin/env python
"""
2021-10-28            Frédéric Dux            first version

This script is to be ran before starting the COSMOULINE pipeline on LCO data. 
As received, the LCO data is organized by date (month, subdirectory day) and the 
filters are mixed together. 

=== example structure of the data as received ===
...
202107
├── ..
202108
├── 10
│   ├── ogg2m001-ep02-20210809-0057-e00.fits.fz
    ...
│   └── ogg2m001-ep05-20210819-0079-e91.fits.fz
├── 21
│   └── ogg2m001-ep05-20210820-0069-e91.fits.fz
│   ...
├── 25
│   ...
└── 31
    ├── ogg2m001-ep02-20210830-0064-e91.fits.fz
    ...
...
=================================================


We want it in this format:
zs
├── (all images in the zs band) 
rp
├── (all images in the rp band) 
ip
├── (all images in the ip band) 
gp
├── (all images in the gp band) 


So that's basically what this script does.
"""
from os         import walk, makedirs, remove
from os.path    import basename, join, splitext
from glob       import glob
from shutil     import move
from astropy.io import fits



indir = '202108'

outdir = 'raw_files'

# First, recursively find all the fits and fits.fz files:
        
files = []
start_dir = indir
pattern   = "*.fits*"

for directory,_,_ in walk(start_dir):
    files.extend(glob(join(directory,pattern))) 
    
# then, we create a directory per filter
filters = {'zs':'', 'rp':'', 'ip':'', 'gp':''}
for f in filters:
    out = join(outdir, f)
    makedirs(out, exist_ok=True)
    filters[f] = out 
    
# now we move all the files one by one in the correct directory. 
for i, f in enumerate(files): 
    
    data    = fits.open(f)[1] 
    name    = basename(f)
    
    ffilter = data.header['FILTER'].strip()
    out     = filters[ffilter]
    
    outpath = join(out, name) 
    if outpath.endswith('.fits.fz'):
        outpathfits = splitext(outpath)[0] 
    
    # and we actually rewrite the fits file as we only need the 
    # second element of the HDU
    # also write it as .fits.fz to keep the compression
    fits.writeto(outpath, data.data, data.header, overwrite=True)
    # but then remove the .fz part so that COSMOULINE sees it.
    if not outpath == outpathfits:
        move(outpath, outpathfits)
        
    # remove the original:
    remove(f)
    print(f"{i+1}/{len(files)}   -  rewrote {f} to {outpathfits}")
    