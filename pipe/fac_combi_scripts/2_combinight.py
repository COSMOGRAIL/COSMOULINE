#
#	second part, we do the combination and we write the header of the images
#
#
#	Viva iraf...
#

execfile("../config.py")
from pyraf import iraf
from kirbybase import KirbyBase, KBError
import shutil
from variousfct import *
import time
from headerstuff import *
import astropy.io.fits as pyfits
import numpy as np

print "You want to combine the images per night of observation for the combiname: %s, using the coeff: %s" %(combiname,renormcoeff)
proquest(askquestions)


if not os.path.isdir(combidir):
	raise mterror("I cannot find the images ... !")

filepath = os.path.join(pipedir, 'fac_combi_scripts/' + 'info_temp.pkl')
listimages = readpickle(filepath)
	

print "I have selected", len(listimages), "images."
proquest(askquestions)
	


# For your info, the default parameters are :

"""
input   =                       List of images to combine
output  =                       List of output images
(headers=                     ) List of header files (optional)
(bpmasks=                     ) List of bad pixel masks (optional)
(rejmask=                     ) List of rejection masks (optional)
(nrejmas=                     ) List of number rejected masks (optional)
(expmask=                     ) List of exposure masks (optional)
(sigmas =                     ) List of sigma images (optional)
(logfile=               STDOUT) Log file

(combine=              average) Type of combine operation
(reject =                 none) Type of rejection
(project=                   no) Project highest dimension of input images?
(outtype=                 real) Output image pixel datatype
(outlimi=                     ) Output limits (x1 x2 y1 y2 ...)
(offsets=                 none) Input image offsets
(masktyp=                 none) Mask type
(maskval=                    0) Mask value
(blank  =                   0.) Value if there are no pixels

(scale  =                 none) Image scaling
(zero   =                 none) Image zero point offset
(weight =                 none) Image weights
(statsec=                     ) Image section for computing statistics
(expname=                     ) Image header exposure time keyword

(lthresh=                INDEF) Lower threshold
(hthresh=                INDEF) Upper threshold
(nlow   =                    1) minmax: Number of low pixels to reject
(nhigh  =                    1) minmax: Number of high pixels to reject
(nkeep  =                    1) Minimum to keep (pos) or maximum to reject (neg)
(mclip  =                  yes) Use median in sigma clipping algorithms?
(lsigma =                   3.) Lower sigma clipping factor
(hsigma =                   3.) Upper sigma clipping factor
(rdnoise=                   0.) ccdclip: CCD readout noise (electrons)
(gain   =                   1.) ccdclip: CCD gain (electrons/DN)
(snoise =                   0.) ccdclip: Sensitivity noise (fraction)
(sigscal=                  0.1) Tolerance for sigma clipping scaling corrections
(pclip  =                 -0.5) pclip: Percentile clipping parameter
(grow   =                   0.) Radius (pixels) for neighbor rejection
(mode   =                   ql)
"""

compter = 0

for i, image in enumerate(listimages):

	iraf.unlearn(iraf.images.immatch.imcombine)
	iraf.images.immatch.imcombine.combine = "median"
	
	print "\n", i+1, " Combining image of night %s" %image["date"]
	
	combinightdir = os.path.join(combidir, image["date"])	#directory that contains the iraf input for the combination, the symlinks on the nonorm images and the images normalized to combine
	
	currentdir =  os.getcwd()
	inputname = "irafinput.txt"
	inputpath = os.path.join(currentdir, inputname)
	
	
	if os.path.isfile(inputpath):		
		os.remove(inputpath)
	os.symlink(os.path.join(combinightdir,inputname), inputpath)
	
	outputname = image["imgname"] +".fits"
	outputpath = os.path.join(combidir, outputname)
	
	if os.path.isfile(outputpath):
		os.remove(outputpath)
		

	iraf.images.immatch.imcombine("@irafinput.txt", output = outputpath)
	
	
	print "\nModifying the header of the images..."
	
	pixelarray, hdr = pyfits.getdata(outputpath, 0, header=True)
	pixelarray = np.asarray(pixelarray).transpose()
	
	if hdr['NCOMBINE'] is not image['ncombine']:
		print "\nIRAF did not combine all the image you wanted because there are more than 8. Viva IRAF!!!!"
		compter += 1	
	
	listcoeff = np.array(image['listcoeff'])
	sum1overcoeff = np.sum(1/listcoeff)

	print "Sum of 1/normcoeff : ", sum1overcoeff

	pixelarray = pixelarray * sum1overcoeff + image['skylevel']	# equivalent to make the sum of the images but a "clean" version of the original images
		
	hdu = pyfits.PrimaryHDU(pixelarray.transpose())			# we clean the header to have only the mandatory fields
	
	for (key, value) in image.iteritems():
		if key == 'listcoeff':
			pass
		else:
			hdu.header.update(key,value)
	
	if os.path.isfile(outputpath):
		os.remove(outputpath)
	
	hdu.writeto(outputpath)
	
	os.remove(inputpath)

if compter is not 0:
	print "Warning: IRAF did not combine correctly %i images."	%compter

print "Done."



