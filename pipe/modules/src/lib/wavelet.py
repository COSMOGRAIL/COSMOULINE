# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#	Functions to play with a-trous-wavelet decompositions of images
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import time
from numpy import *
from scipy import signal
import utils as fn

out = fn.Verbose()

# 2D cubic spline coeffs
csplinefilter2d = array(
[[1./256, 1./64, 3./128, 1./64, 1./256], 
[1./64, 1./16, 3./32, 1./16, 1./64], 
[3./128, 3./32, 9./64, 3./32, 3./128],
[1./64, 1./16, 3./32, 1./16, 1./64], 
[1./256, 1./64, 3./128, 1./64, 1./256]
])
# 1D cubic spline coeffs
csplinefilter1d = array([[1./16., 1./4., 3./8., 1./4., 1./16.]])
# 2D triangle function coeffs
trifilter2d = array([[1./16, 1./8, 1./16], [1./8, 1./4, 1./8], [1./16, 1./8, 1./16]])
# 1D triangle function coeffs
trifilter1d = array([[1./4., 1./2., 1./4.]])


haar=array([[1., -1.]])

def timing(func):
	# A quick and dirty timing, as some operations in this module might take a while...
	def wrapper(*args, **kwargs):
		t1 = time.time()
		res = func(*args, **kwargs)
		t2 = time.time()
		mstaken = (t2-t1)*1000.0 # milliseconds
		
		if mstaken < 1000.:
			print '+++ timing : function %s took %0.2f ms' % (func.func_name, mstaken)
		elif mstaken < 60000.:
			print '+++ timing : function %s took %0.2f s' % (func.func_name, mstaken/1000.0)
		else:	
			print '+++ timing : function %s took %0.2f min' % (func.func_name, mstaken/60000.0)
		return res
	return wrapper

def percetrous(infilter, level, newshape=None):
	# This function expands a filter by adding "trous", for the "a trous" wavelet transform.
	# A filter is a 2D numpy array.
	# We return the expanded filter as a new, larger array.
	
	
	# Calculate dimensions of the output filter
	insize1 = infilter.shape[0]
	outsize1 = insize1 + (insize1-1) * (2**level - 1)
	insize2 = infilter.shape[1]
	outsize2 = insize2 + (insize2-1) * (2**level - 1)
	
	# Start with zeroes 
	outfilter = zeros((outsize1,outsize2), dtype=float64)
	
	# Put the coefficients at the right places 
	for i in range(0,insize1):
		for j in range(0, insize2):
			outfilter[i*(2**level), j*(2**level)] = infilter[i,j]
	
	if newshape is not None:
		tmp = zeros(newshape)
		l = outfilter.shape[0]
		begin = (newshape[0]-l)//2
		tmp[begin:begin+l,begin:begin+l] = outfilter
		tmp = fn.switch_psf_shape(tmp, 'SW')
		return tmp
	return outfilter

#@timing
def atrous(image, infilter=csplinefilter2d, levels=3, conv_fn=None):
	# Calculates the a-trous wavelet decomposition : input = mtimage, ouptut = list of mtimages of components.
	# This is version 0.0.1 ... direct space non-separable convolution.
	
	# outimgs[0] = input image
	# outimgs[1:-2] = coefficients (as many as there are levels)
	# outimgs[-1] = last smoothed image
	# In other words : outimgs[0] = Sum of outimgs[1:]
		
	outimgs = []
	outimgs.append(image) # first element = original image
	conved = image.copy()
	for l in range(0, levels):
		trousfilter = percetrous(infilter, l, image.shape)
		if conv_fn is not None:
			reconved = conv_fn(trousfilter, conved)
		else:
			reconved = signal.convolve2d(conved, trousfilter, mode="same", boundary="symm")
		diff = conved - reconved
		outimgs.append(diff)
		conved = reconved
		out(4, "Level", l+1, "done.")
	outimgs.append(reconved)
	
	return outimgs

#@timing
def sepatrous(image, infilter=csplinefilter1d, levels=3):
	# Same as atrous()
	# But separable -> a lot faster
	
	outimgs = []
	outimgs.append(image) # first element = original image
	
	conved = image.copy()
	for l in range(0, levels):
		trousfilter = percetrous(infilter, l)
		reconved = signal.convolve2d(conved, trousfilter, mode="same", boundary="symm")
		reconved = signal.convolve2d(reconved, trousfilter.transpose(), mode="same", boundary="symm")
		diff = conved - reconved
		outimgs.append(diff)
		conved = reconved
#		print "+++ wavelet decomp. : level", l+1, "done."
	outimgs.append(reconved)
	
	return outimgs

@timing
def fftatrous(image, infilter=csplinefilter2d, levels=3):
	# Same as atrous()
	# But with FFT. No symmetric boundary condition.
	# Very bad, as the of image is computed for every wavelet ...
	
	outimgs = []
	outimgs.append(image) # first element = original image
	
	conved = image.copy()
	for l in range(0, levels):
		trousfilter = percetrous(infilter, l)
		reconved = signal.fftconvolve(conved, trousfilter, mode="same")
		diff = conved - reconved
		outimgs.append(diff)
		conved = reconved
		print "+++ wavelet decomp. : level", l+1, "done."
	outimgs.append(reconved)
	
	return outimgs


def reconstructiontest(atrousoutlist):
	# Takes the "outimgs" list of images made by the atrous functions, and compares the original input
	# to the result of reconstruction from wavelet transform
	
	orig = atrousoutlist[0].array
	rec = zeros(orig.shape)
	for i in range(1, len(atrousoutlist)):
		rec += atrousoutlist[i].array
	null = rec - orig
	
	print "+++ reconstructiontest : mean =", mean(null)
	print "+++ reconstructiontest : stddev =", std(null)
	return mtimage(null) #@UndefinedVariable

@timing
def logwavecombi(atrousoutimg, epsilon):
	combi = zeros(atrousoutimg[0].array.shape, dtype=float64)
	for i in range(1, len(atrousoutimg)-1):
		combi += sign(atrousoutimg[i].array) * log10(abs(atrousoutimg[i].array) + epsilon)
	combi += sign(atrousoutimg[-1].array) * log10(abs(atrousoutimg[-1].array) + epsilon)
	return mtimage(combi) #@UndefinedVariable



def mylog(inarray):

	inmin = inarray.min()
	inmax = inarray.max()
	outarray = inarray.copy()
	outarray = outarray.clip(0.0, inmax)
	outarray = log10(10.0 + 990.0 * (outarray - inmin))
	return outarray		

@timing	
def experimentalcombi(atrousoutimg, epsilon):
	combi = zeros(atrousoutimg[0].array.shape, dtype=float64)
	for i in range(1, len(atrousoutimg)-1):
		combi += mylog(atrousoutimg[i].array)
	#combi += mylog(atrousoutimg[-1].array)
	
	
	#combi = sign(atrousoutimg[2].array) * log10(abs(atrousoutimg[2].array) + 1.)
	
	return mtimage(combi)	#@UndefinedVariable








