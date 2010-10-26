"""
TEST to imporove the sextractor reliability...
Facultative : we look for plain "0" cols and lines, and fill them for random noise.
"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import pyfits
import cosmics # used to read and write the fits files


db = KirbyBase()
images = db.select(imgdb, ['flagali','gogogo','treatme'], ['==1',True, True], ['recno','imgname'], sortFields=['imgname'], returnType='dict')

print "I will treat %i images." % len(images)
proquest(askquestions)

for n, image in enumerate(images):

	print n+1, "/", len(images), ":", image['imgname']
	
	aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
	
	(a, h) = cosmics.fromfits(aliimg, verbose=False)
	
	zeroa = a == 0
	cols = zeroa.a(axis = 0)
	lins = zeroa.a(axis = 1)
	a[cols,:] = np.random.randn(a.shape[1])*image["stddev"]
	a[:,lins] = np.random.randn(a.shape[0])*image["stddev"]
	
	cosmics.tofits(aliimg, a, h, verbose=False)

	
notify(computer, withsound, "Done.")

