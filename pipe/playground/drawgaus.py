import numpy as np
import astropy.io.fits as pyfits

def fromfits(filename):
	return pyfits.getdata(filename).transpose()

def tofits(a, filename):
	pyfits.writeto(filename, a.transpose(), clobber=1)


def gaus(shape, theta, fwhm, e, c1, c2, i0):
	_cos = np.cos(theta)
	_sin = np.sin(theta)
	xm = lambda x,y: (x-c1)*_cos - (y-c2)*_sin
	ym = lambda x,y: (x-c1)*_sin + (y-c2)*_cos
	sigx = fwhm / (2. * np.sqrt(2.*np.log(2.)))
	sigy = sigx /(1. - e**2)
	g = lambda x,y: i0*np.exp(-(xm(x,y)/(np.sqrt(2.)*sigx))**2. - (ym(x,y)/(np.sqrt(2.)*sigy))**2.)
	return np.fromfunction(g, shape)
	

a = np.zeros((128, 128))
#a = fromfits("dec0001.fits")

a += gaus(a.shape, 1.9, 2.5, 0.4, 67, 64.1, 100.0)

a += gaus(a.shape, 1.9, 10.0, 0.4, 66.0, 65.0, 100.0)


tofits(a, "backbi.fits")