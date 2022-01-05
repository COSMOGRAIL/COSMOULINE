#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 16:36:33 2021


This script makes a plot of night medians , by seeing, of your current objkey, 
after extraction.
If you have muliple bands, you can compare the seeing in each band directly.

@author: frederic dux
"""
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))


from   pathlib           import   Path
import numpy             as       np
from   astropy.io        import   fits
import matplotlib.pyplot as       plt

from   kirbybase         import   KirbyBase


db = KirbyBase()
workdir = Path(workdir) 
keydir  = workdir / objkey
allimages = db.select(imgdb, ['gogogo', 'treatme'], 
                             [ True,     True], 
                             returnType='dict', 
                             sortFields=['setname', 'seeing'])



def getNights(allimages, setname):
    """
       sorts images by observation night.
       
       returns: a dictionnary of indexes per night
    """
    names  = [im['imgname'] for im in allimages if im['setname'] == setname]
    nights = {}
    for i, e in enumerate(names):
        night = e.split('-')[2]
        if not night in nights:
            nights[night] = [i]
        else:
            nights[night].append(i)
    return nights

# work by setname (band):
setnames   = list(set([im['setname'] for im in allimages]))
nights     = {}
medseeings = {}
medarrays  = {}
for setname in setnames:
    nights[setname]     = getNights(allimages, setname)
    medseeings[setname] = [ np.median([ allimages[i]['seeing'] 
                                       for i in nights[setname][night]]) 
                                            for night in nights[setname].keys()  ]
    # calculate the median per night:
    medarrays[setname]  = [ np.median([ fits.getdata((keydir/allimages[i]['imgname'])/'g.fits')  
                                           for i in nights[setname][night] ], axis=0) 
                                                for night in nights[setname].keys() ]

#%%
N = 5
quantiles = np.linspace(0, 1, N)

fig, axs = plt.subplots(N, len(setnames), figsize=(10,17))

for j,row in enumerate(axs):
    quantile = quantiles[j]
    try:
        iter(row)
    except:
        row = [row]
    for i, ax in enumerate(row):
        if j == 0:
            ax.set_title("band: "+ setname)
        ax.set_yticks([])
        ax.set_xticks([])
        
        setname = setnames[i]
        seeing   = np.quantile(medseeings[setname], quantile)
        index    = np.argmin(np.abs(np.array(medseeings[setname])-seeing))
        
        data    = medarrays[setname][index][10:-10, 10:-10]
        vmin, vmax = np.percentile(data, (2, 99.9))
        ax.imshow(data, vmin=vmin, vmax=vmax)
        ax.set_ylabel(f"quantile: {quantile:.1f} \nseeing: {seeing:.1f}\" ")
        
plt.tight_layout()
