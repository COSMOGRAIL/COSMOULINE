#!/usr/bin/python


from lib.AImage import *
from lib.Star import *
from lib.Param import *
from lib.Algorithms import *
import lib.utils as fn
import lib.wsutils as ws
from numpy import *
import numpy as np
import scipy.ndimage.interpolation, copy

out = fn.Verbose()

PAR = Param(1, 0)
STAR_COL = []
TRACE = []

def fitnum(fit_id, data, params, savedir = 'results/'):
    global PAR
    global STAR_COL
    global TRACE
    
    starpos, npix, sfactor, mpar = params['STARS'], params['NPIX'], params['S_FACT'], copy.deepcopy(params['MOF_PARAMS'])
    gres, fitrad, psf_size, itnb =  params['G_RES'], params['FIT_RAD'], params['PSF_SIZE'], params['MAX_IT_N']
    nbruns, show, lamb, stepfact = params['NB_RUNS'], params['SHOW'], params['LAMBDA_NUM'], params['BKG_STEP_RATIO_NUM']
    cuda, radius, stddev = params['CUDA'], params['PSF_RAD'], params['SIGMA_SKY'] 
    
    PAR = Param(1, 0)
    STAR_COL = []
    TRACE = []
    mofpar = Param(1, 0)
    bshape = data['stars'][fit_id][0].shape
    sshape = (int(bshape[0]*sfactor), int(bshape[1]*sfactor))
    ini = zeros(sshape, dtype=float64)
#    nbruns=1
    
    
    if cuda and fn.has_cuda():
        out(2, 'CUDA initializations')
        context, plan = fn.cuda_init(sshape)
        r_len = sshape[0]
        r = fn.gaussian((r_len, r_len), gres, r_len/2-1, r_len/2-1, 1.)
        r = fn.switch_psf_shape(r, 'SW')
        def conv(a, b):
            return fn.cuda_conv(plan, a, b)
    else:
        conv = fn.conv
        r_len = math.pow(2.0,math.ceil(math.log(gres*10)/math.log(2.0)))
        r = fn.gaussian((r_len, r_len), gres, r_len/2-1, r_len/2-1, 1.)
        cuda = False
    r /= r.sum()
    
    for i, pos in enumerate(starpos):           
            #populates the stars array:
#            im = Image(copy.deepcopy(data['stars'][fit_id][i]), noisemap = copy.deepcopy(data['sigs'][fit_id][i])) 
            im = Image(data['stars'][fit_id][i].copy(), noisemap = data['sigs'][fit_id][i].copy()) 
            im.shiftToCenter(mpar[fit_id][4+3*i]/sfactor,mpar[fit_id][4+3*i+1]/sfactor, center_mode='O')
            mpar[fit_id][4+3*i:4+3*i+2] = sshape[0]/2., sshape[1]/2. 
            STAR_COL += [Star(i+1, im, mofpar, sfactor, gres, False)]
    mofpar.fromArray(array(mpar[fit_id]), i = -1)
    mof_err = 0.
    for s in STAR_COL:
#        s.nm_mod = True
        if fitrad is not None:
            c1, c2 = bshape[0]/2., bshape[1]/2.
            img = zeros(s.image.array.shape, dtype=float64)
            img[c1-fitrad//2 : c1+fitrad//2,
                c2-fitrad//2 : c2+fitrad//2] = s.image.array[c1-fitrad//2 : c1+fitrad//2,
                                                             c2-fitrad//2 : c2+fitrad//2]
            s.image.array = img
        s.moff_eval()
        s.build_diffm()
        f_nm = s.image.noiseMap.sum()
#        f_d = s.diffm.array.sum()
        f_i = s.image.array.sum()
        s.image.array = scipy.ndimage.interpolation.zoom(s.image.array, sfactor, order = 5, mode='reflect')
        s.image.array *= f_i/s.image.array.sum()
        #TODO: check if the order is correct:
        s.image.noiseMap = scipy.ndimage.interpolation.zoom(s.image.noiseMap, sfactor, order = 5, mode='reflect')
        s.image.noiseMap *= f_nm/s.image.noiseMap.sum()
        s.diffm.array = s.image.array - s.psfm.array
#        s.diffm.array = scipy.ndimage.interpolation.zoom(s.diffm.array, sfactor, order = 5, mode='reflect')
#        s.diffm.array *= f_d/s.diffm.array.sum()
        s.image.noiseMap /= mpar[fit_id][6+3*(s.id-1)]
        s.diffm.array /= mpar[fit_id][6+3*(s.id-1)]
        ini += s.diffm.array
        mof_err += abs(s.diffm.array).sum()
    ini /= 5.*len(STAR_COL)
    
    
    def _errfun(bkg, null):
        global TRACE
        param = bkg.reshape(sshape)
        err = zeros(sshape, dtype=float64)
        convo = conv(r, param)
        for s in STAR_COL:
            err += lamb*((s.diffm.array - convo)/s.image.noiseMap)**2. + (param - convo)**2.
        TRACE += [err.sum()]
        return err.ravel()
    
    out(2, 'Begin minimization procedure')
    t = time.time()
    
    
    npar = ini.copy()
    for i in xrange(nbruns):
        npar = minimi(_errfun, npar.ravel(),[], itnb=itnb//nbruns, stepfact=stepfact)[0][0]
#        npar = minimi_num(_errfun, npar, itnb=itnb//nbruns, stepfact=stepfact)[0]
        out(2)
    bak = npar.reshape(sshape)
    out(2, 'Done in', time.time()-t,'[s]')
    
#    bak, lbak = minimi_brute(_errfun, ini, itnb=itnb)#, stddev=sigma[0]/100000.)
#    out(2)
#    out(2, 'Done in', time.time()-t,'[s]')
    
    convo = conv(r, bak)
    gaus_err = convo*0.
    for s in STAR_COL:
        gaus_err += abs(s.diffm.array - convo)
    gaus_err = gaus_err.sum()
    out(2, "indicative error gain:", 100*(1. - TRACE[-1]/TRACE[0]), "%")#gaus_err/mof_err), "%")  

    out(2, 'Building the final PSF...')
    #TODO: use the center option!!
    if psf_size is not None:
        psf = PSF((psf_size*sfactor, psf_size*sfactor))
        psf.addMof_fnorm(mpar[fit_id][0:4]+[psf.c1, psf.c2, 1.])
        psf.array[psf.c1-bak.shape[0]//2 : psf.c1+bak.shape[0]//2,
                  psf.c2-bak.shape[1]//2 : psf.c2+bak.shape[1]//2] += bak
    else:
        psf = PSF((npix*sfactor, npix*sfactor))
        psf.addMof_fnorm(mpar[fit_id][0:4]+[psf.c1, psf.c2, 1.])
    #    psf.set_finalPSF(mpar[fit_id][0:4], [], [], 'mixed')
        psf.array += bak
    psf.normalize()
    
    if savedir is not None:
        out(2, 'Writing PSF to disk...')
        Image(fn.switch_psf_shape(psf.array)).writetofits(savedir+"s_"+str(fit_id+1)+".fits")
        Image(psf.array).writetofits(savedir+"psf_"+str(fit_id+1)+".fits")
        fn.array2fits(bak, savedir+'psfnum.fits')
        for s in STAR_COL:
            resi = (s.diffm.array-conv(r,bak))/s.image.noiseMap
            fn.array2fits(resi, savedir+"difnum%(n)02d.fits" % {'n': s.id})
    if show == True:
        out(2, 'Displaying results...')
        fn.array2ds9(psf.array, name='psf')
        fn.array2ds9(bak, name='psfnum', frame=2)
        i = 3
        for s in STAR_COL:
            s.diffm.showds9(ds9frame=i,imgname="difm_"+str(s.id))
            resi = (s.diffm.array-conv(r,bak))/s.image.noiseMap
            fn.array2ds9(resi, frame=i+1, name="resi_"+str(s.id))
            if savedir is not None:
                fn.array2fits(resi, savedir+"difnum%(n)02d.fits" % {'n': s.id})
            i += 2
        import pylab as p
        p.figure(1)
        trace = array(TRACE)
        X = arange(trace.shape[0])
        p.title('Error evolution')
        p.plot(X, trace)
        p.show()
        if savedir is not None:
            p.savefig(savedir+'trace%(fnb)02d.png'% {'fnb':fit_id+1})

    if cuda:
        out(2, 'Freeing CUDA context...')
        context.pop()
    return 0


    
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
    if 'e' in opt: 
        import prepare
        prepare.main(['_3_fitmof.py', '-ce', cfg])
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    out(1, 'Begin background fit')
    PSF_SIZE = None
    SHOW = False
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME', 'SHOW', 'STARS','NPIX', 'MOF_PARAMS', 
            'G_PARAMS', 'G_POS', 'G_STRAT', 'S_FACT', 'NOWRITE', 
            'G_RES', 'CENTER', 'IMG_GAIN', 'SIGMA_SKY',
            'SKY_BACKGROUND', 'G_SETTINGS', 'NB_RUNS', 'FIT_RAD']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        return 1
    out(2, 'Restore data from extracted files')
    files, cat = ws.get_multiplefiles(FILENAME, 'img')
    fnb = len(cat)
    data = ws.restore(*ws.getfilenames(fnb))
    data['filenb'] = fnb
    data['starnb'] = len(STARS)
    gpar = []
    gpos = []
    for i in xrange(fnb):
        out(1, '===============', i+1, '/', fnb,'===============')
        out(1, 'Working on', files[i])
        fitnum( i, data, locals())
    out(1, '------------------------------------------')
    out(1, 'Numerical fit done')
#    if NOWRITE is False:
#        fn.write_cfg(cfg, {'G_PARAMS':gpar, 'G_POS':gpos})
    return 0
    
    
def profile():
    # This is the main function for profiling 
    import cProfile, pstats
    prof = cProfile.Profile()
    prof = prof.runctx("main()", globals(), locals())
    stats = pstats.Stats(prof)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(15)  # how many to print
    # The rest is optional.
    #stats.print_callees()
    #stats.print_callers()
    
if __name__ == "__main__":
    #sys.exit(profile())
    sys.exit(main())

    