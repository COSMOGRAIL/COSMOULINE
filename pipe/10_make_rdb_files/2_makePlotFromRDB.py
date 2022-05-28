#!/usr/bin/env python
"""
    Script building a nice plot of some light curves contained in a rdb file.
"""

import pycs3
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import settings, configdir

##############################################################################
##############################################################################
##############################################################################
# first plot without transformation to get the idea of the time range, etc:
roughplot      = 0
# import the data - execute the script once for each dataset separately. 
fullname       = settings['lensName']
telescopename  = settings['telescopename']
# names of the curves to be imported from the rdb file:
lcsnames       = settings['sourcenames']
# Shift the lcs in mag for display purposes:
# Huge shift (30) to make the mag positive, roughly about the expectation (19)
# Small shift (-0.6) to make the lcs closer to each other 
# and better display the variations
globalmagshift = 30
# individual shift of each curve: one shift per lcsname. 
shifts         = [0, -0.5]
# limits of the axes:
jdrange        = [59360, 59600]
magrange       = [18.09, 17.77]
# paths to your data directory and rdb file:
rdbfile        = os.path.join(configdir, settings['outputname'] + '.rdb')
# path to where the plots will be saved 
# (the file extension, e.g. `pdf` will be added automatically!)
plotpath       = os.path.join(configdir, f"{settings['outputname']}_Nice_Plot")
##############################################################################
##############################################################################
##############################################################################



# read each light curve. 
lcs = []
for lc in lcsnames:
    curve = pycs3.gen.lc_func.rdbimport(rdbfile, f'{lc}', f'mag_{lc}', 
                                        f'magerr_{lc}_5', telescopename)
    lcs.append(curve)

# set individual colors:
pycs3.gen.mrg.colourise(lcs)

# (optional) display them, to make sure everything looks OK.
# also useful to get the limits of the axes.
if roughplot:
    pycs3.gen.lc_func.display(lcs, showdates=True)


# now building the plot, adjusting the positions on the graph ...
disptext = []

for ind, (lc, shift) in enumerate(zip(lcs, shifts)):
    # apply the magnitude shift:
    lc.shiftmag(globalmagshift + shift)
    
    # elements will be placed relative to the first point of the curve:
    firstpt = (lc.getjds()[0], lc.getmags()[0])
   
    # name of the curve:
    xcoord = (firstpt[0] - 90 - jdrange[0]) / (jdrange[1] - jdrange[0])
    ycoord = (firstpt[1] + 0.02 - magrange[0]) / (magrange[1] - magrange[0])
    txt    = lcsnames[ind]
    colour = lc.plotcolour
    kwargs = {"fontsize": 22, "color": lc.plotcolour}
    disptext.append((xcoord, ycoord, txt, kwargs))
    
    # additional text (here shift of the curve)
    xcoordadd = (firstpt[0]  - 90 - jdrange[0])  / (jdrange[1] - jdrange[0])
    ycoordadd = (firstpt[1] +0.09 - magrange[0]) / (magrange[1] - magrange[0])
    txtadd    = shift
    colouradd = lc.plotcolour
    kwargsadd = {"fontsize": 14, "color": lc.plotcolour}
    disptext.append((xcoordadd, ycoordadd, txtadd, kwargsadd))


# display the figure: once on the screen, then in a png file, then pdf:
displays     = ["screen", plotpath + '.png', plotpath + '.pdf']

for display in displays:
    pycs3.gen.lc_func.display(lcs, title=r"$\mathrm{" + fullname + "}$", 
                              jdrange=jdrange, magrange=magrange,
                              filename=display, transparent=False, 
                              text=disptext, style='homepagepdfnologo')
import matplotlib.pyplot as plt
plt.show()
