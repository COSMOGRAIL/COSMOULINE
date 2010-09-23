#
#	How to import and play with sextractor catalogs ...
#	For more details, see http://www.stecf.org/software/PYTHONtools/astroasciidata/

from pylab import *
import asciidata

mycat = asciidata.open('large.cat')

#	Some examples to get the idea
#print mycat.info()
#print mycat.nrows, mycat.ncols
#print mycat['FWHM_IMAGE'].info()
#print mycat['FWHM_IMAGE'].get_type()

#	work with the data

fwhms = sorted(mycat['FWHM_IMAGE'].tonumpy())
seeingestimation = median(fwhms[:int(len(fwhms)/2.)]) # median of the "first half"

#	and make a simple plot

hist(fwhms, facecolor='green', alpha=0.75, bins=arange(0,10,0.1))

axvline(x=seeingestimation, linewidth=2, color='r')
figtext(0.4, 0.65, r'$\mathrm{Seeing\ :\ FWHM}\ \approx \ %2.2f\ \mathrm{[pixels]}$'%seeingestimation, fontsize=16, color='r')
xlabel("FWHM [pixels]")
title("Seeing histogram")
grid(True)

show()

