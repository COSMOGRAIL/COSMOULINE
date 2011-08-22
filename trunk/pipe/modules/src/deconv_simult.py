#!/usr/bin/python

import sys, time, scipy.optimize, scipy.ndimage.interpolation
import scipy.ndimage.filters as filt

import src.lib.utils as fn
import src.lib.wsutils as ws
import src.lib.Algorithms as alg
import scipy.signal.signaltools as sig
from src.lib.PSF import *
from src.lib.AImage import *
from src.lib.wavelet import *
from src.lib.deconv import *
from numpy import *
from copy import deepcopy

out = fn.Verbose()
CUDA = False

def deconv(data, params, savedir='results/'):
    global err, old_bkg, TRACE, TRACE2, err_bk, err_sm
    err = old_bkg = None
    
    sfact, gres, itnb, mpar = params['S_FACT'], params['G_RES'], params['MAX_IT_D'], params['MOF_PARAMS']
    gstrat, gpar, gpos = params['G_STRAT'], params['G_PARAMS'], params['G_POS']
    show, maxpos_range, stddev = params['SHOW'], params['MAXPOS_RANGE'], params['SIGMA_SKY']
    max_iratio_range, force_ini = params['MAX_IRATIO_RANGE'], params['FORCE_INI']
    bkg_ini, stepfact, bkg_ratio = params['BKG_INI_CST'], params['BKG_STEP_RATIO'], params['BKG_START_RATIO']
    _lambda, nbruns, nb_src = params['LAMBDA'], params['D_NB_RUNS'], params['NB_SRC']
    box_size, src_range, cuda = params['BOX_SIZE'], params['SRC_RANGE'], params['CUDA']
    srcini, minstep_px, maxstep_px = params['INI_PAR'], params['MIN_STEP_D'], params['MAX_STEP_D']
    thresh = params['WL_THRESHOLD_DEC']

    out(2, 'Initialization')
    nimg = params['filenb']
    objs = [data['objs'][i][0].astype('float64') for i in xrange(nimg)]
    sigmas = [data['objssigs'][i][0].astype('float64') for i in xrange(nimg)]
    masks = [data['objsmasks'][i][0].astype('float64') for i in xrange(nimg)]
    psfs = [data['psfs'][i][0].astype('float64') for i in xrange(nimg)]
    dev = stddev[0]
    mpar = mpar[0]
    gpar = gpar[0]
    gpos = gpos[0]
    bshape = objs[0].shape
    sshape = (int(bshape[0]*sfact), int(bshape[1]*sfact))
    sources = [PSF(sshape, (sshape[0]/2., sshape[1]/2.)) for i in xrange(nimg)]
    
    ############### Prepare the gaussian PSF ###############
    r_len = sshape[0]
    c1, c2 =  r_len/2.-0.5, r_len/2.-0.5 #-0.5 to align on the pixels grid
    r = fn.gaussian(sshape, gres, c1, c2, 1.)
#    r = fn.LG_filter(sshape, gres, c1, c2)
    if cuda and fn.has_cuda():
        out(2, 'CUDA initializations')
        context, plan = fn.cuda_init(sshape)
        r = fn.switch_psf_shape(r, 'SW')
        def conv(a, b):
            return fn.cuda_conv(plan, a, b)
        def div(a, b):
            return fn.cuda_fftdiv(plan, a, b)
        psfs = [fn.switch_psf_shape(p, 'SW') for p in psfs]
    else:
        conv = fn.conv
        div = None#fn.div
        cuda = False
    r /= r.sum()
    div = None

    ########## Initializations ########## 
    img_shifts = fn.get_shifts(objs, 10.)
    _lambda = fn.get_lambda(sshape, None, _lambda)
#    if not thresh:
#        thresh = params['SIGMA_SKY']
    dec = DecSrc(objs, sigmas, masks, psfs, r, conv, img_shifts, _lambda, 
                 gres, thresh, nb_src, srcini, box_size, src_range, force_ini,
                 bkg_ini, bkg_ratio)
    

    ########## Deconvolution ########## 
    bak, src_par = dec.deconv(itnb, minstep_px, maxstep_px,
                 maxpos_range, max_iratio_range, stepfact, nbruns)
    out(2, 'Initial sources parameters [x,y,I]:', dec.src_ini)
    out(2, 'Final sources parameters [x,y,I]:', src_par) 
    out(2, 'offsets:', dec.shifts)
    
    ############ Prepare output ############
    imgs, names = [], []
    imgs += [bak, dec.ini]
    names += ['background', 'bkg_ini']   
    dec.set_sources(src_par, bak)
    for i in xrange(len(objs)):        
        bak_conv = conv(dec.psfs[i], bak+dec.sources[i].array)
        resi = dec.get_im_resi(bak_conv, i)
        imgs += [objs[i], resi, dec.sources[i].array, bak+dec.sources[i].array]
        names += ["g_"+str(i+1), 
                  "resi_%(fnb)02d" % {'fnb':i+1},
                  "sources_%(fnb)02d" % {'fnb':i+1},
                  "deconv_%(fnb)02d" % {'fnb':i+1}]
        
    ############ Save and display ############
    if savedir is not None:
        out(2, 'Writing to disk...')
        for i, im in enumerate(imgs):
            fn.array2fits(im, savedir+names[i]+'.fits')
#        fn.save_img(imgs, names, savedir+'overview.png', min_size=(256,256))
    if show == True:
        out(2, 'Displaying results...')
        for i, im in enumerate(imgs):
            fn.array2ds9(im, name=names[i], frame=i+1)
            
    import pylab as p
    p.figure(1)
    trace = array(dec.trace)
    X = arange(trace.shape[0])
    p.title('Error evolution')
    p.plot(X, trace)
#    p.legend()
    p.draw()
    p.savefig(savedir+'trace_deconv.png')
    if show == True:
        p.show()

    if cuda:
        out(2, 'Freeing CUDA context...')
        context.pop()
        
    return src_par, dec.shifts, dec.src_ini

          
def main(argv=None):
    cfg = 'config.py'
    if argv is not None:
        sys.argv = argv
    opt, args = fn.get_args(sys.argv)
    MAX_IT_D = MAXPOS_STEP = MAX_IRATIO_STEP = SHOW = FORCE_INI = None
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
    if 'i' in opt: 
        FORCE_INI = True
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    out(1, 'Begin deconvolution process')
    
    #TODO: check workspace
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME', 'MAX_IT_D', 'S_FACT', 'G_RES', 'SIGMA_SKY',
            'MOF_PARAMS', 'G_STRAT', 'G_PARAMS', 'G_POS', 'CENTER']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        return 1
    out(2, FILENAME) #@UndefinedVariable
    out(2, 'Restore data from extracted files')
    fnb = ws.get_filenb(FILENAME) #@UndefinedVariable
    files = ws.getfilenames(fnb)
    data = ws.restore(*files)
    data['filenb'] = fnb
    dec = deconv(data, locals())
#    if NOWRITE is False:
#        fn.write_cfg(cfg, {'DEC_PAR':dec})
    out(1, 'Deconvolution done')
    
    return 0
    
    
if __name__ == "__main__":
#    import cProfile, pstats
#    prof = cProfile.Profile()
#    prof = prof.runctx("main()", globals(), locals())
#    stats = pstats.Stats(prof)
#    stats.sort_stats("time")  # Or cumulative
#    stats.print_stats(15)  # how many to print
    sys.exit(main())


