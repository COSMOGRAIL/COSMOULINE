#!/usr/bin/python
from copy import deepcopy

import sys, time
#import lib.imutils as imu
#import lib.io_utils as io
import lib.utils as fn
import lib.wsutils as ws
import lib.Algorithms as alg
from lib.PSF import *
from lib.AImage import *
from lib.wavelet import *
import numpy
from numpy import *
import scipy.optimize
import scipy.ndimage.interpolation
import scipy.signal as signal
import scipy.signal.signaltools as sig
#import psyco
#psyco.full()

out = fn.Verbose()
CUDA = False

def _get_ini_bkg(data, levels=4, conv_fn=None):
#    wl = sepatrous(data, trifilter2d, levels=levels)
    wl = atrous(data, trifilter2d, levels=levels, conv_fn= conv_fn)
    bk =wl[-1] + wl[-2]# + wl[-3] + wl[-4]
#    bk = wl[0] - (wl[1] + wl[2] + wl[3] + wl[4])
    bk *= (bk>=0.) #no neg constraint
    return bk
    
     
def _get_ini(img, sig, psf, nb_src, gres, sfact, nimg=1, ores=None, 
             src_range=None, convol=fn.conv, fft_div=None, pad=5.):
    data = img.copy()
    resi_bk = img.copy()
    refpar = 0., 0.
    if fft_div:
        out(3, 'FFT division...')
        dec = fft_div(psf, data)
        dec_bk = dec.copy()
        ini_bkg = dec.copy()
        
        def __errfun(param):
            resi = (dec - fn.gaussian(data.shape, param[0], param[1], param[2], param[3]))#/sig
            resi *= (100000.*(param[3]<0.)+1.)
            resi *= ((100. * (resi < 0.)) + 1.)
            resi *= (100000.*(abs(param[1]-refpar[0])>2. or abs(param[2]-refpar[1])>2.) + 1.)
            return (resi**2.).ravel()
    else:
        out(3, 'Wavelet decomposition...')
        ini_bkg = _get_ini_bkg(data, conv_fn=convol)
#        resi_bk -= ini_bkg
        def __errfun(param):
            resi = (data - convol(psf,fn.gaussian(data.shape, param[0], param[1], param[2], param[3])))#/sig
            resi *= (100000.*(param[3]<0.)+1.)
            resi *= ((100. * (resi < 0.)) + 1.)
            resi *= (100000.*(abs(param[1]-refpar[0])>2. or abs(param[2]-refpar[1])>2.) + 1.)
            return (resi**2.).ravel()
    srcpos = array(fn.getGpos(resi_bk, nb_src, pad, cutoffs=src_range)[0])
    ret = array([])
    for i, p in enumerate(srcpos):
        out(3, 'Getting initial parameters for source', i+1, '-r')
        if fft_div:
            xx, xy = maximum(p[0]-2.*pad, 0), minimum(p[0]+2.*pad, img.shape[0]-1)
            yx, yy = maximum(p[1]-2.*pad, 0), minimum(p[1]+2.*pad, img.shape[1]-1)
            data = resi_bk[xx:xy, yx:yy]
            dec = dec_bk[xx:xy, yx:yy]
            ini = [gres, 2.*pad, 2.*pad, resi_bk[p[0], p[1]]]
            refpar = 2.*pad, 2.*pad
        else:
            data = resi_bk
            ini = [gres, p[0], p[1], resi_bk[p[0], p[1]]]
            refpar = p[0], p[1]
        gini = scipy.optimize.leastsq(__errfun, ini)[0]
        if fft_div:
            gini[1] += xx
            gini[2] += yx
        resi_bk -= convol(psf,fn.gaussian(resi_bk.shape, gini[0], gini[1], gini[2], gini[3]))
        if fft_div:
            dec_bk -= fn.gaussian(dec_bk.shape, gini[0], gini[1], gini[2], gini[3])
        gini[3] = gini[3]*gini[0]**2./gres**2.
        ret = append(ret, gini[1:])
    out(3, 'Done!')
    if fft_div:
        return ret.reshape((nb_src, 3)), dec_bk
    return ret.reshape((nb_src, 3)), ini_bkg#resi_bk 
        
def set_ini(data, params):
    #TODO: set to the new norms!! (params)
    def X2x(X):
        return X*sfact - 1./sfact
    def x2X(x):
        return x/sfact + 1./sfact**2.
    nimg, sfact, gres = params['filenb'],params['S_FACT'], params['G_RES']
    show, USE_CUDA, nb_src = params['SHOW'], params['CUDA'], params['NB_SRC']
    box_size, src_range, fftdiv = params['BOX_SIZE'], params['SRC_RANGE'], params['FFT_DIV']
    
    obj = [data['objs'][i][0].astype('float64') for i in xrange(nimg)]
    sigma = [data['objssig'][i][0].astype('float64') for i in xrange(nimg)]
    psf = [data['psfs'][i][0].astype('float64') for i in xrange(nimg)]
    bshape = obj[0].shape
    sshape = (int(bshape[0]*sfact), int(bshape[1]*sfact))
    
    orig_fwhm = 4.5 # 4. #BIG pixels! ~3.
    
    if USE_CUDA and fn.has_cuda():
        context, plan = fn.cuda_init(sshape)
        out(2, 'CUDA initializations')
        def convol(a, b):
            return fn.cuda_conv(plan, a, b)
        def deconv(a, b):
            return fn.cuda_fftdiv(plan, a, b)
        if not fftdiv:
            deconv = None
    else:
        USE_CUDA = False
        convol = fn.conv
        deconv = None
    
    out(2, 'Interpolating data...')
    obji = []
    sigmai = []
    flux_o = []
    flux_s = []
    for i in xrange(nimg):
        d_filt = signal.signaltools.wiener(obj[i], [3,3])
#        psf[i] = signal.signaltools.medfilt2d(psf[i], [3,3])
#        psf[i] /= psf[i].sum()
        obji += [scipy.ndimage.interpolation.zoom(d_filt, sfact, order = 5, mode='reflect').astype('float64')]
        sigmai += [scipy.ndimage.interpolation.zoom(sigma[i], sfact, order = 5, mode='reflect').astype('float64')]
        flux_o += [obj[i].sum()]
        flux_s += [sigma[i].sum()]
        obji[i] *= flux_o[-1]/obji[i].sum()
        sigmai[i] *= flux_s[-1]/sigmai[i].sum()

    out(2, 'Setting initial sources parameters...')
    srcpos, ini = _get_ini(obji[0], sigmai[0], psf[0], nb_src, gres, sfact, nimg, orig_fwhm, 
                           src_range, convol, deconv, pad=box_size)
    
    shiftpar = -fn.get_shifts(obj, boxsize=10)[1:]#array([0.1 for i in xrange(2*nimg)])
    shiftpar = shiftpar.ravel()
    
    fn.array2fits(ini, 'results/bkg_ini.fits')    
    ws.drop('INI_PAR', srcpos)
    if show:
        fn.array2ds9(obji[0], name='data')
        fn.array2ds9(ini, name='background', frame=2)
    if USE_CUDA:
        out(2, 'Freeing CUDA context...')
        context.pop()
    return ini, srcpos, shiftpar
    


def main(argv=None):
    cfg = 'config.py'
    if argv is not None:
        sys.argv = argv
    opt, args = fn.get_args(sys.argv)
    if args is not None: cfg = args[0]
    if 's' in opt: 
        out.level = 0
    if 'v' in opt: 
        out.level = 2
    if 'd' in opt: 
        DEBUG = True
        out.level = 3
        out(1, '~~~ DEBUG MODE ~~~')
    if 'b' in opt: 
        import prepare
        prepare.main(['deconv.py', '-b', cfg])
    if 'e' in opt: 
        import prepare
        prepare.main(['deconv.py', '-ce', cfg])
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    out(1, 'Begin initialization')
    
    #TODO: check workspace
    CONV_IT = MAXPOS_STEP = MAX_IRATIO_STEP = SHOW = None
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME', 'CONV_IT', 'S_FACT', 'G_RES', 'SIGMA_SKY',
            'MOF_PARAMS', 'G_STRAT', 'G_PARAMS', 'G_POS', 'CENTER']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        return 1
    out(2, FILENAME)
    out(2, 'Restore data from extracted files')
    fnb = ws.get_filenb(FILENAME)
    files = ws.getfilenames(fnb)
    data = ws.restore(*files)
    data['filenb'] = fnb
    set_ini(data, locals())
#    if NOWRITE is False:
#        fn.write_cfg(cfg, {'DEC_PAR':dec})
    out(1, 'Initialization done')
    
    return 0
    
    
if __name__ == "__main__":
#    import cProfile, pstats
#    prof = cProfile.Profile()
#    prof = prof.runctx("main()", globals(), locals())
#    stats = pstats.Stats(prof)
#    stats.sort_stats("time")  # Or cumulative
#    stats.print_stats(15)  # how many to print
    sys.exit(main())


