"""
TEST to improve PSF fitting, flux measurements and so on...

As sextractor skysub is a bit too efficient, we correct all the pixels by the mean value of the empty region

Not sur if it is really useful, though...

TODO : look at firedec way to correct from the median sky, and implement it here.
"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import pyfits
import numpy as np
import cosmics # used to read and write the fits files


db = KirbyBase()
images = db.select(imgdb, ['flagali','gogogo','treatme'], ['==1',True, True], ['recno','imgname', 'stddev', 'emptymean'], sortFields=['imgname'], returnType='dict')

print "I will treat %i images." % len(images)
#proquest(askquestions)

for n, image in enumerate(images):

	print n+1, "/", len(images), ":", image['imgname']
	
	aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")

	(aliarray, aliheader) = fromfits(aliimg, verbose=False)
	aliarray -= image['emptymean']


	tofits(aliimg, aliarray, aliheader, verbose=False)

print "The sky substraction has been corrected ! "

notify(computer, withsound, "Done.")

