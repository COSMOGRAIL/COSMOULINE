import numpy as np
import astropy.io.fits as pyfits


def fromfits(filename):
	return pyfits.getdata(filename).transpose()

def tofits(a, filename):
	pyfits.writeto(filename, a.transpose(), clobber=1)


def haar(img):
	"""
	Single level Haar wavelet decomposition 
	"""
	s = (img[1::2,:] + img[0::2,:])/2.
	d = img[0::2,:] - img[1::2,:]
	ss = (s[:,1::2] + s[:,0::2])
	sd = s[:,0::2] - s[:,1::2] 
	ds = (d[:,1::2] + d[:,0::2])/2.
	dd = (d[:,0::2] - d[:,1::2])/2.
	return [ss, sd, ds, dd]

def ihaar(coeffs):
	"""
	Inverse single level Haar
	"""
	(ss, sd, ds, dd) = coeffs
	s = np.zeros((ss.shape[0], 2*ss.shape[1]))
	s[:,1::2] += (ss - sd)/2.0
	s[:,0::2] += (ss + sd)/2.0
	d = np.zeros((ds.shape[0], 2*ds.shape[1]))
	d[:,1::2] += ds - dd
	d[:,0::2] += ds + dd
	out = np.zeros((2*s.shape[0], s.shape[1]))
	out[1::2,:] += s - d/2.0
	out[0::2,:] += s + d/2.0
	return out

def multihaar(img, levels = None):
	"""
	Multilevel Haar wavelet decomposition
	Assumes image is square and width is power of 2 !
	Returns a list of list of "coeffs", length = number of levels.
	Warning : these "coeffs" also contain the SS image at each level, so they are redundant !
	The structure of the output is the following :
	[[L1_SS, L1_SD, L1_DS, L1_DD], [L2_SS, L2_SD, L2_DS, L2_DD], [L3_SS, L3_SD, L3_DS, L3_DD]]
	where "L1" is the top (= finest) level, and "L(N)_SS" is further decomposed in the next level as "L(N+1)_XX".
	Apart from the structure, the output is numerically identical to the one from pywt.
	"""
	if levels == None: # then we go as deep as possible
		levels = int(np.log2(img.shape[0]))
	output = [haar(img)]
	for l in range(levels-1):
		output.append(haar(output[-1][0]))
	return output

def imultihaar(coeffs):
	"""
	Inverse multilevel Haar.
	We reconstruct the image starting with the deepest level, using only non-redundant coefficients.
	In other words, we disregard all the SS images, except of the deepest one.
	"""
	mycoeffs = coeffs[::-1] # copy + invert
	mycoeffs.append([None, None, None, None])
	for l in range(len(mycoeffs)-1):
		#print l, mycoeffs[l][0].shape
		mycoeffs[l+1][0] = ihaar(mycoeffs[l])
	return mycoeffs[-1][0]
	
def mallat(coeffs):
	"""
	Puts together the "Mallat"-like image of the coefs.
	"""
	mycoeffs = coeffs[::-1] # copy + invert
	mycoeffs.append([None, None, None, None])
	for l in range(len(mycoeffs)-1):
		#print l, mycoeffs[l][0].shape
		mycoeffs[l+1][0] = np.concatenate([np.concatenate([mycoeffs[l][1], mycoeffs[l][0]], axis=1), np.concatenate([mycoeffs[l][3], mycoeffs[l][2]], axis=1)], axis=0)
	
	return mycoeffs[-1][0]
	


def circshift(inimg, shift):
	"""
	inimg : numpy array
	shift : (xshift, yshift)
	"""
	return np.roll(np.roll(inimg, shift[0], axis = 0), shift[1], axis = 1)




def cyclespin(inimg, nb_lvl, ts=None, shiftlevel=None):
	"""
	inimg : numpy array, must be square
	ts : a list of thresholds
	shiftlevel : number of levels you want to be fully translation invariant. Default is len(ts).
	"""
	if ts is None:
		ts = inimg.std()
	ts = [ts*0.7**i for i in xrange(nb_lvl)]
	
	if shiftlevel == None:
		shiftlevel = len(ts)
	nlinshifts = 2**shiftlevel
	nlinimg = inimg.shape[0]
	
	# We build a list of shifts to perform :
	shifts = [np.array([a, b]) for a in range(nlinshifts) for b in range(nlinshifts)]
	
	# We build the big image containing all the shifted versions :
	bigimg = np.zeros((nlinimg*nlinshifts, nlinimg*nlinshifts))
	for shift in shifts:
		bigimg[shift[0]*nlinimg:(shift[0]+1)*nlinimg, shift[1]*nlinimg:(shift[1]+1)*nlinimg] = circshift(inimg, shift)
	
	# Do the WT :
	bigimgwt = multihaar(bigimg, levels=shiftlevel)
	#print len(bigimgwt)
	
	# The hard thresholding
	for (i,t) in enumerate(ts):
		#print shiftlevel-i-1
		bigimgwt[i][1][np.abs(bigimgwt[i][1]) <= t] = 0.0
		bigimgwt[i][2][np.abs(bigimgwt[i][2]) <= t] = 0.0
		bigimgwt[i][3][np.abs(bigimgwt[i][3]) <= t] = 0.0
		
	# IWT :
	bigrec = imultihaar(bigimgwt)
	
	# Shift back and stack :
	output = [circshift(bigrec[shift[0]*nlinimg:(shift[0]+1)*nlinimg, shift[1]*nlinimg:(shift[1]+1)*nlinimg], -shift) for shift in shifts]
	output = np.mean(output, axis = 0)
	return output




def htdenoise(img, thresholds, csshift = (0,0)):
	"""
	returns a denoised images, made with hard thresholds ts on the len(ts) first levels.
	csshifts are "cycle spinning shifts" that are applied in x and y prior (and posterior) to the denoising.
	To use cyclespinning, pass this function to cyclespinmap.
	"""
	imgwt = multihaar(circshift(img, csshift), levels=len(thresholds))
	for (i,t) in enumerate(thresholds):
		imgwt[i][1][np.abs(imgwt[i][1]) <= t] = 0.0
		imgwt[i][2][np.abs(imgwt[i][2]) <= t] = 0.0
		imgwt[i][3][np.abs(imgwt[i][3]) <= t] = 0.0
	return circshift(imultihaar(imgwt), (-csshift[0], -csshift[1]))
	
	
def cyclespinmap(img, denoisingfct, n, **kwargs):
	"""
	n is the number of levels to cyclespin, set this to the number of levels you use in the denoising.
	denoisingfct takes an image and returns a denoised one, and must have a keyword argument "csshift".
	Any further kwargs are passed to denoisingfct
	"""
	# We build a list of shifts to perform :
	shifts = [np.array([a, b]) for a in range(2**n) for b in range(2**n)]
	# Apply the denoising :
	denoised = map(lambda shift: denoisingfct(img, csshift=shift, **kwargs), shifts)
	# Return the mean image :
	return np.mean(denoised, axis = 0)


def postpsfnumcs(img, t = 10.0):
	"""
	Quick and dirty, for hard coded experiements ...
	t is a threshold in units of sigma, the higher the smoother
	"""
	
	#return img * 0.0 # For tests, to "skip" the numerical part ...
	
	# We evaluate the model's noise by looking at the image borders ...
	bs = 3
	borderpixels = np.concatenate([img[:bs,:].ravel(), img[-bs:,:].ravel(), img[:,:bs].ravel(), img[:,-bs:].ravel()])
	modelsigma = np.std(borderpixels.ravel())
	
	# We build some thresholds for the n first wavelet levels :
	nlevels = 4 # number of levels to consider
	#t = 10.0 # threshold in units of sigma 
	thresholds = [t * modelsigma * (0.7**i) for i in range(nlevels)]
	#thresholds[0] = t * modelsigma * 1.6
	
	# And run a cyclespinning of hard thresholds
	return cyclespinmap(img, htdenoise, n = nlevels, thresholds = thresholds)


		

import scipy.ndimage.interpolation

def pixelbuster(img, csshift = (0,0)):
	"""
	Remove "big pixels", i.e. ugly 2x2 squares, by estimating haar coeffs for the first level.
	Note that by default we attack only big pixels that are not shifted with respect to simple 2x2 binning.
	If you have big pixels at random location, you might want to cyclespin this function.
	"""
	
	imgwt = multihaar(circshift(img, csshift), levels=2)
	for i in [1,2,3]:
		# The second level coeffs :
		ref = imgwt[1][i]
		# We upsample them without any interpolation (hmm, works, but could be better)
		#upref = ref[tuple(np.mgrid[0:ref.shape[0]:0.5, 0:ref.shape[1]:0.5].astype("int"))]
		# We upsample them with linear interpolation :
		upref = scipy.ndimage.interpolation.zoom(ref, 2, order=1)
		# The coeffs that should be improved :
		bigpixindices = np.abs(imgwt[0][i]) == 0
		# Set the new coeffs
		imgwt[0][i][bigpixindices] = upref[bigpixindices]/4.0
		
	return circshift(imultihaar(imgwt), (-csshift[0], -csshift[1]))



