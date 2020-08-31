"""
TEST to imporove the sextractor reliability...
Facultative : we look for plain "0" cols and lines, and fill them for random noise.

It seems to work.

"""

execfile("../config.py")
from kirbybase import KirbyBase, KBError
from variousfct import *
import numpy as np
import cosmics # used to read and write the fits files
import multiprocessing

def fillnoise(n, image, n_im_tot): 
	print n+1, "/", n_im_tot, ":", image['imgname']
	
	aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")
	
	(a, h) = cosmics.fromfits(aliimg, verbose=False)
	
	zeroa = a <= (0.01 * image["stddev"])
	cols = zeroa.all(axis = 0)
	lins = zeroa.all(axis = 1)
	
	colsshape = a[:,cols].shape
	a[:,cols] = (np.random.randn(colsshape[0] * colsshape[1])*image["stddev"]).reshape(colsshape)
	
	linsshape = a[lins,:].shape
	a[lins,:] = (np.random.randn(linsshape[0] * linsshape[1])*image["stddev"]).reshape(linsshape)
	
	cosmics.tofits(aliimg, a, verbose=False)
	
def fillnoise_aux(args):
    return fillnoise(*args)

db = KirbyBase()
if update:
	print "This is an update."
	images = db.select(imgdb, ['flagali','gogogo','treatme', 'updating'], ['==1',True, True, True], ['recno','imgname', 'stddev'], sortFields=['imgname'], returnType='dict')
	askquestions=False
else:
	images = db.select(imgdb, ['flagali','gogogo','treatme'], ['==1',True, True], ['recno','imgname', 'stddev'], sortFields=['imgname'], returnType='dict')

print "I will treat %i images." % len(images)
proquest(askquestions)

n_im_tot = len(images)

ncorestouse = multiprocessing.cpu_count()
#~ ncorestouse = forkmap.nprocessors()
if maxcores > 0 and maxcores < ncorestouse:
	ncorestouse = maxcores
	print "maxcores = %i" % maxcores
print "For this I will run on %i cores." % ncorestouse

pool = multiprocessing.Pool(processes = ncorestouse)
job_args = [(n, image, n_im_tot) for n, image in enumerate(images)]

pool.map(fillnoise_aux, job_args)
pool.close()
pool.join()

notify(computer, withsound, "Done.")


