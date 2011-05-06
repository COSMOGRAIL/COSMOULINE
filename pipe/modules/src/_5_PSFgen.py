#!/usr/bin/python


from numpy import *
#import lib.utils as fn
from lib.PSF import *
#from lib.AImage import *
import sys
import lib.utils as fn
import lib.wsutils as ws

out = fn.Verbose()

def psf_gen(fit_id, params):
    
    gstrat, sfact, mpar = params['G_STRAT'], params['S_FACT'], params['MOF_PARAMS']
    psfsize, g_par, g_pos =  params['PSF_SIZE'], params['G_PARAMS'], params['G_POS']
    show, objsize = params['SHOW'], params['OBJ_SIZE']

    out(2, 'Initialization...')
#    if psfsize is None: psfsize = objsize
#    nx = ny = psfsize*sfact
#    if center == 'O':
#        c1, c2 = nx/2.-0.5, ny/2.-0.5
#    elif center == 'NE':
#        c1, c2 = nx/2., ny/2.
#    elif center == 'SW':
#        c1, c2 = nx/2.-1., ny/2.-1.
#    psf = PSF((nx,ny), (c1,c2))
#    mof = mpar[fit_id][:4]
#    gpos = array(g_pos)[fit_id]
#    gpar = array(g_par)[fit_id]
#    out(2, 'Building the PSF...')
#    psf.set_finalPSF(mof, gpar, gpos, gstrat, (c1, c2, 1.), center=center)
#    out(2, 'Done. Creating splitted PSF (old style shape)...')
#    s = fn.switch_psf_shape(psf.array, center)
    size = psfsize*sfact, psfsize*sfact
    psf, s = fn.psf_gen(size, zeros(size), mpar[fit_id][:4], array(g_par)[fit_id], 
                        array(g_par)[fit_id], gstrat, sfact)
    fn.array2fits(psf.array, 'results/psf_'+str(fit_id+1)+'.fits')
    fn.array2fits(s, 'results/s_'+str(fit_id+1)+'.fits')
    if show == True:
        fn.array2ds9(psf.array, name='psf')
        fn.array2ds9(s, name='s', frame=2)



def main(argv=None):
    cfg = 'config.py'
    span = None
    if argv is not None:
        sys.argv = argv
    if len(sys.argv) >1:
        cfg = sys.argv[1]
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['NPIX', 'MOF_PARAMS',  'S_FACT', 'G_PARAMS', 
            'G_POS', 'G_STRAT', 'CENTER', 'PSF_SIZE', 'OUT']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        return 1
    fnb = ws.get_filenb(FILENAME)
    for i in xrange(fnb):
        psf_gen(i, locals())
    return 0
    
    
if __name__ == "__main__":
    sys.exit(main())
