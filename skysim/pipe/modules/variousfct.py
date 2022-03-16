import pickle


def writepickle(obj, filepath, verbose=True):

	
	"""
	I write your python object into a pickle file at filepath.
	"""
	outputfile = open(filepath, 'wb')
	pickle.dump(obj, outputfile)
	outputfile.close()
	if verbose:
		print "Wrote %s" % filepath


def readpickle(filepath, verbose=True):
	

	"""
	I read a pickle file and return whatever object it contains.
	"""
	pkl_file = open(filepath, 'rb')
	obj = pickle.load(pkl_file)
	pkl_file.close()
	if verbose:
		print "Read %s" % filepath
	return obj


# FITS import - export
# 
# def fromfits(infilename, hdu = 0, verbose = True):
# 	"""
# 	Reads a FITS file and returns a 2D numpy array of the data.
# 	Use hdu to specify which HDU you want (default = primary = 0)
# 	"""
# 	
# 	pixelarray, hdr = pyfits.getdata(infilename, hdu, header=True)
# 	pixelarray = np.asarray(pixelarray).transpose()
# 	
# 	pixelarrayshape = pixelarray.shape
# 	if verbose :
# 		print "FITS import shape : (%i, %i)" % (pixelarrayshape[0], pixelarrayshape[1])
# 		print "FITS file BITPIX : %s" % (hdr["BITPIX"])
# 		print "Internal array type :", pixelarray.dtype.name
# 	
# 	return pixelarray, hdr
# 
# def tofits(outfilename, pixelarray, hdr = None, verbose = True):
# 	"""
# 	Takes a 2D numpy array and write it into a FITS file.
# 	If you specify a header (pyfits format, as returned by fromfits()) it will be used for the image.
# 	You can give me boolean numpy arrays, I will convert them into 8 bit integers.
# 	"""
# 	pixelarrayshape = pixelarray.shape
# 	if verbose :
# 		print "FITS export shape : (%i, %i)" % (pixelarrayshape[0], pixelarrayshape[1])
# 
# 	if pixelarray.dtype.name == "bool":
# 		pixelarray = np.cast["uint8"](pixelarray)
# 
# 	if os.path.isfile(outfilename):
# 		os.remove(outfilename)
# 	
# 	if hdr == None: # then a minimal header will be created 
# 		hdu = pyfits.PrimaryHDU(pixelarray.transpose())
# 	else: # this if else is probably not needed but anyway ...
# 		hdu = pyfits.PrimaryHDU(pixelarray.transpose(), hdr)
# 
# 	hdu.writeto(outfilename)
# 	
# 	if verbose :
# 		print "Wrote %s" % outfilename	
# 


	
