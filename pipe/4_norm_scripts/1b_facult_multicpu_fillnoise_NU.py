"""
TEST to imporove the sextractor reliability...
Facultative : we look for plain "0" cols and lines, and fill them for random noise.

It seems to work.

"""

import multiprocessing
import numpy as np
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import alidir, computer, imgdb, settings
from modules.kirbybase import KirbyBase
from modules import cosmics
from variousfct import notify, proquest

askquestions = settings['askquestions']
emptyregion = settings['emptyregion']
maxcores = settings['maxcores']

def fillnoise(n, image, n_im_tot):
    print(n + 1, "/", n_im_tot, ":", image['imgname'])

    aliimg = os.path.join(alidir, image['imgname'] + "_ali.fits")

    (a, h) = cosmics.fromfits(aliimg, verbose=False)

    zeroa = a <= (0.01 * image["stddev"])
    cols = zeroa.all(axis=0)
    lins = zeroa.all(axis=1)

    colsshape = a[:, cols].shape
    a[:, cols] = (np.random.randn(colsshape[0] * colsshape[1]) * image["stddev"]).reshape(colsshape)

    linsshape = a[lins, :].shape
    a[lins, :] = (np.random.randn(linsshape[0] * linsshape[1]) * image["stddev"]).reshape(linsshape)
    
    # second step. 
    # in some cases we'll have regions with no data (NaNs).
    # fill these with noise as well. 
    mask = np.where(np.isnan(a))
    npix = len(mask[0])
    a[mask] = np.random.randn(npix) * image["stddev"]

    cosmics.tofits(aliimg, a, verbose=False)


def fillnoise_aux(args):
    return fillnoise(*args)


def main():
    db = KirbyBase(imgdb)
    if settings['update']:
        print("This is an update.")
        images = db.select(imgdb, ['flagali', 'gogogo', 'treatme', 'updating'], ['==1', True, True, True],
                           ['recno', 'imgname', 'stddev'], sortFields=['imgname'], returnType='dict')
    else:
        images = db.select(imgdb, ['flagali', 'gogogo', 'treatme'], ['==1', True, True], ['recno', 'imgname', 'stddev'],
                           sortFields=['imgname'], returnType='dict')

    print("I will treat %i images." % len(images))
    proquest(askquestions)

    n_im_tot = len(images)

    ncorestouse = multiprocessing.cpu_count()
    if maxcores > 0 and maxcores < ncorestouse:
        ncorestouse = maxcores
        print("maxcores = %i" % maxcores)
    print("For this I will run on %i cores." % ncorestouse)

    pool = multiprocessing.Pool(processes=ncorestouse)
    job_args = [(n, image, n_im_tot) for n, image in enumerate(images)]

    pool.map(fillnoise_aux, job_args)
    pool.close()
    pool.join()

    notify(computer, settings['withsound'], "Done.")


if __name__ == '__main__':
    main()
