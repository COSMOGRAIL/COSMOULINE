"""
Draw analytical background for a lens
Also compute the precise astometry for your telescope pixel size
"""

import numpy as np
import os,sys
import pyfits
import scipy


# Astrometry : e.g. from Castles survey
# in arcseconds

A = (0, 0)
B = (1.257, -0.056)
G1 = (0.437, 0.018)


pixsize = 0.2149
arcsectopix = 1.0 / pixsize


# astrometry. Give initial coordinates for A in pixels, I compute B, C, D and G coordinates in pixels according to your astrometry and the pixel size of the images

if 1:
	Ainit_x = 33.155209   # in pixels
	Ainit_y = 33.650440  # in pixels

	A_pix = ((-A[0]*arcsectopix)+Ainit_x, (A[1]*arcsectopix)+Ainit_y)
	B_pix = ((-B[0]*arcsectopix)+Ainit_x, (B[1]*arcsectopix)+Ainit_y)
	G1_pix = ((-G1[0]*arcsectopix)+Ainit_x, (G1[1]*arcsectopix)+Ainit_y)

	print "A", '\t', A_pix[0], '\t', A_pix[1]
	print "B", '\t', B_pix[0], '\t', B_pix[1]
	print "G1", '\t', G1_pix[0], '\t', G1_pix[1]

	#sys.exit()


# draw a background
if 0:
	# canvas is a black 128x128 pixels fits file
	os.system('cp canvas.fits back.fits')  # background to pass to MCS
	os.system('cp canvas.fits profile.fits')  # non-convolved profile, 128*128
	os.system('cp canvas.fits gaussian.fits')  # gaussian, 128*128

	profile = pyfits.open('profile.fits', mode='update')
	gaussian = pyfits.open('gaussian.fits', mode='update')
	back = pyfits.open('back.fits', mode='update')

	data = back[0].data
	pdata = profile[0].data
	gdata = gaussian[0].data

	# Sersic profile parameters - main lens
	I0 = 2000   # arbitrary
	#reff_arcsec = 1.5
	#reff_pix = reff_arcsec * arcsectopix * 2.0  # *2 as we use finer pixels
	reff_pix = 0.2
	xc = G1_pix[0] * 2.0  # *2 as we use finer pixels
	yc = G1_pix[1] * 2.0  # idem

	# Sersic profile parameters - companion
	I0_comp = 500   # arbitrary
	#reff_arcsec_comp = 1.5
	#reff_pix_comp = reff_arcsec_comp * arcsectopix * 2.0  # *2 as we use finer pixels
	reff_pix_comp = 0.1
	xc_comp = G2_pix[0] * 2.0  # *2 as we use finer pixels
	yc_comp = G2_pix[1] * 2.0  # idem


	# Sersic profile
	def getprofilevalue(x, y, xc, yc, I0, reff_pix, sersic_index=4.0):
		r = np.sqrt((x-xc)**2 + (y-yc)**2)
		return I0*np.exp(-(r/reff_pix)**(1.0/sersic_index))

	# Read data value
	def getfitsvalue(data, x, y):
		return data[x][y]

	# 2D gaussian profile
	fwhm = 2.0  # pixels
	sigma = fwhm / 2.355
	def get2dgaussianvalue(x, y, xc, yc):
		return 1.0 / (2 * np.pi * sigma ** 2) * np.exp(-((x - xc) ** 2 + (y - yc) ** 2) / (2 * sigma ** 2))

	for lind, line in enumerate(gdata):
		for cind, elt in enumerate(line):
			gdata[lind][cind] = get2dgaussianvalue(cind+1, lind+1, 65, 65)
			pdata[lind][cind] = getprofilevalue(cind+1, lind+1, xc, yc, I0, reff_pix) + getprofilevalue(cind+1, lind+1, xc_comp, yc_comp, I0_comp, reff_pix_comp)

	import scipy.ndimage

	if 1:
		out = scipy.ndimage.filters.convolve(gdata, pdata)
		for lind, line in enumerate(data):
			for cind, elt in enumerate(line):
				data[lind][cind] = out[lind][cind]


		back.close()
		profile.close()
		gaussian.close()
		sys.exit()



	from scipy.optimize import minimize

	########## NOT WORKING WELL ###########
	if 0:
		xs = np.arange(0, 128, 1)
		ys = np.arange(0, 128, 1)
		fitsdata = pyfits.open('optimised.fits')[0].data
		fitsval = getfitsvalue(fitsdata, xs, ys)


		def tominim((vals)):
			I0 = vals[0]
			reff_pix = vals[1]
			sersic_index = vals[2]
			for lind, line in enumerate(gdata):
				for cind, elt in enumerate(line):
					pdata[lind][cind] = getprofilevalue(cind+1, lind+1, I0, reff_pix, sersic_index)
			convol = scipy.ndimage.filters.convolve(gdata, pdata)
			res = 0.0
			for l1, l2 in zip(convol, fitsval):
				for c1, c2 in zip(l1, l2):
					res += np.sqrt((c1 - c2) ** 2)
			return res


		def tominimtest((vals)):
			x = vals[0]
			y = vals[1]
			return (x-1) **2 + (y-2) **2



		#print tominim([1000, 1.0])
		#print tominim(1000, 0.2)
		#sys.exit()
		min = minimize(tominim, ([8000, 0.01, 4.5]), bounds=((2000, 10000), (0.01, 0.3), (3, 5)))

		#min = minimize(tominimtest, ([6,6]), bounds=((2,3), (2,12)))
		print min.x
		print min.success

		# OPTIMUM PARAMETERS FROM MINIMIZE :[  9.67585375e+02   9.83258231e-02]
		# OPTIMUM PARAMETERS FROM MINIMIZE :[  5.00351033e+03   2.84755113e-02]
		# OPTIMUM PARAMETERS FROM MINIMIZE :[  5.00142905e+03   3.00398690e-02   3.97002517e+00] # I used this one !
		# OPTIMUM PARAMETERS FROM MINIMIZE :[  8.00000000e+03   1.15868793e-02   4.32036352e+00]
		sys.exit()




	# Let's do something stupid and simple (like me!): brute force optimisation:
	if 0:
		def leastsq(data1, data2):
			res = 0.0
			for l1, l2 in zip(data1, data2):
				for c1, c2 in zip(l1, l2):
					res += np.sqrt((c1 - c2) ** 2)
			return res

		I0s = np.arange(4000, 8000, 1000)
		reffs = np.arange(0.01, 0.2, 0.02)
		sersics = np.arange(3.5, 4.5, 0.2)
		xs = np.arange(0, 128, 1)
		ys = np.arange(0, 128, 1)

		fitsdata = pyfits.open('optimised.fits')[0].data
		fitsval = getfitsvalue(fitsdata, xs, ys)
		resmin = 1e10

		for indI0, I0 in enumerate(I0s):
			for indreff, reff in enumerate(reffs):
				for sersic in sersics:
					for lind, line in enumerate(pdata):
						for cind, elt in enumerate(line):
							pdata[lind][cind] = getprofilevalue(cind+1, lind+1, I0, reff, sersic)
					convol = scipy.ndimage.filters.convolve(gdata, pdata)
					res = leastsq(convol, fitsval)
					print I0, reff, sersic, res
					if res < resmin:
						resmin = res
						I0min = I0
						reffmin = reff
		print 'Min results: I0 = ', I0min, ' | reff = ', reffmin

		sys.exit()





	if 0:
		toplot = pyfits.open('back.fits')[0].data

		# Display stuff, slow...
		from matplotlib import cm
		from matplotlib.ticker import LinearLocator, FormatStrFormatter
		import matplotlib.pyplot as plt
		from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization!
		import numpy as np

		fig = plt.figure()
		ax = Axes3D(fig)
		X = np.arange(0,128,1)
		Y = np.arange(0,128,1)
		Z = getfitsvalue(toplot, X, Y)
		X, Y = np.meshgrid(X, Y)
		#Z = getprofilevalue(128-X, Y)
		#Z = getconvolution(X, Y)
		surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
				linewidth=0, antialiased=False)


		ax.zaxis.set_major_locator(LinearLocator(10))
		ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

		fig.colorbar(surf, shrink=0.5, aspect=5)
		plt.show()

