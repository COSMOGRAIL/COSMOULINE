#!/usr/bin/python

import sys, time, scipy.optimize, scipy.ndimage.interpolation
import scipy.ndimage.filters as filt

import src.lib.utils as fn
import src.lib.wsutils as ws
import src.lib.Algorithms as alg
import scipy.signal.signaltools as sig
from lib.PSF import *
from lib.AImage import *
from lib.wavelet import *
from numpy import *
from copy import deepcopy

out = fn.Verbose()
CUDA = False
TRACE = []

def _get_ini(data, sig, psf, params, nb_src, gres, sfact, nimg=1, ores=None, 
             src_range=None, convol=fn.conv, div=fn.div, pad=5., force_ini=False):
    import get_ini_par as init
    #TODO: generic for multiple images
    #TODO: bkgini as parameter
    img = data
    srcini = params['INI_PAR']
    try: 
        bkgini = fn.get_data('bkg_ini.fits')
        force_ini += (len(srcini)/3. != nb_src)
#        srcini[3*nb_src-1]
    except:
        force_ini = True
    if force_ini:
        out(3, 'Beginning initialization from scratch...')
        srcpos, bkgini = init._get_ini(img, sig, psf, nb_src, gres, sfact, nimg, ores, 
                                       src_range, convol, div, pad)
        ws.drop('INI_PAR', srcini)
        fn.array2fits(bkgini, 'results/bkg_ini.fits')    
        srcini = []
        for i,p in enumerate(srcpos): 
            if i==nb_src or nb_src==0: #tmp
                break
    #        srcini += [X2x(p[1]),X2x(p[2])]
            srcini += [p[0],p[1]]
            for j in xrange(nimg):
                srcini += [p[2]]
    srcini = array(srcini)
    return srcini, bkgini
    
    
def deconv(data, params):
    global err, old_bkg, TRACE
    err = old_bkg = None
    TRACE = []
    
    sfact, gres, itnb, mpar = params['S_FACT'], params['G_RES'], params['MAX_IT_D'], params['MOF_PARAMS']
    gstrat, gpar, gpos = params['G_STRAT'], params['G_PARAMS'], params['G_POS']
    show, maxpos_range, stddev = params['SHOW'], params['MAXPOS_RANGE'], params['SIGMA_SKY']
    max_iratio_range, force_ini = params['MAX_IRATIO_RANGE'], params['FORCE_INI']
    bkg_ini, stepfact, bkg_ratio = params['BKG_INI_CST'], params['BKG_STEP_RATIO'], params['BKG_START_RATIO']
    _lambda, nbruns, nb_src = params['LAMBDA'], params['D_NB_RUNS'], params['NB_SRC']
    box_size, src_range, cuda = params['BOX_SIZE'], params['SRC_RANGE'], params['CUDA']
    def X2x(X):
        return X*sfact - 1./sfact
    def x2X(x):
        return x/sfact + 1./sfact**2.
    out(2, 'Initialization')
    nimg = params['filenb']
    obj = [data['objs'][i][0].astype('float64') for i in xrange(nimg)]
    sigma = [data['objssig'][i][0].astype('float64') for i in xrange(nimg)]
    psf = [data['psfs'][i][0].astype('float64') for i in xrange(nimg)]
    dev = stddev[0]
    mpar = mpar[0]
    gpar = gpar[0]
    gpos = gpos[0]
    bshape = obj[0].shape
    sshape = (int(bshape[0]*sfact), int(bshape[1]*sfact))
#    nx, ny = bshape
    
    ### legacy, te be cleaned ###
    trust_threshold = 1.
    orig_fwhm = 5. # 4. #BIG pixels! ~3.
    #############################
    
    _totit = itnb*nbruns
    maxpos_step= maxpos_range / (_totit+(_totit==0))
    max_iratio_step= max_iratio_range / (_totit+(_totit==0))
    
#    for i in xrange(nimg):  
#        s = obj[i].sum()
#        obj[i] /= s
#        sigma[i] /= s
    
    
    if cuda and fn.has_cuda():
        out(2, 'CUDA initializations')
        context, plan = fn.cuda_init(sshape)
        r_len = sshape[0]
        r = fn.gaussian((r_len, r_len), gres, r_len/2-1, r_len/2-1, 1.)
#        r = fn.gaussian((r_len, r_len), gres, r_len/2-1, r_len/2-1, 1.)
        r = fn.switch_psf_shape(r, 'SW')
        def convol(a, b):
            return fn.cuda_conv(plan, a, b)
        def div(a, b):
            return fn.cuda_fftdiv(plan, a, b)
    else:
        convol = fn.conv
        div = None#fn.div
        r_len = math.pow(2.0,math.ceil(math.log(gres*10)/math.log(2.0)))
        r = fn.gaussian((r_len, r_len), gres, r_len/2-1, r_len/2-1, 1.)
        cuda = False
    r /= r.sum()
    
    div = None
    
    sources = [PSF(sshape, (sshape[0]/2., sshape[1]/2.)) for i in xrange(nimg)]

    out(2, 'Interpolating data...')
    obji = []
    sigmai = []
    flux_o = []
    flux_s = []
    ini = zeros(sshape)
    for i in xrange(nimg):
        obji += [scipy.ndimage.interpolation.zoom(obj[i], sfact, order = 5, mode='reflect').astype('float64')]
        sigmai += [scipy.ndimage.interpolation.zoom(sigma[i], sfact, order = 5, mode='reflect').astype('float64')]
        flux_o += [obj[i].sum()]
        flux_s += [sigma[i].sum()]
        obji[i] *= flux_o[-1]/obji[i].sum()
#        out(2, 'Setting initial background parameters...')
        sigmai[i] *= flux_s[-1]/sigmai[i].sum()
#        ini += obji[i]*bkg_ratio
#    ini /= nimg
#    
#    ini = obji[0]*bkg_mul #TODO: get a better solution
#    ini = ini*0. + bkg_ini
#    ini = ini*0. + dev/(abs(obji[0]/sigmai[0]))
#    ini *= 0. + 50. #TODO: get a better solution
#    ini = ini/10.#*0. + median(obji[0])#.std()*obji[0]/sigmai[0]

    out(2, 'Setting initial sources parameters...')
    imult = (orig_fwhm*sfact/gres)**2.
    err = zeros(sshape)
    ###############
    srcini, ini = _get_ini(obji[0], sigmai[0], psf[0], params, nb_src, gres, sfact, nimg, orig_fwhm, 
                                         src_range, convol, div, pad=box_size, force_ini=force_ini)
    #TODO: eliminate the bypass:
    shiftpar_ini = -fn.get_shifts(obj, boxsize=10)[1:]#array([0.1 for i in xrange(2*nimg)])
    shiftpar_ini = shiftpar_ini.ravel()
#    ini = obji[0]
#    srcpos = []
    ################
    ini *= bkg_ratio
    if bkg_ini:
        ini = ini*0. + bkg_ini
    oldsrc = srcini*1.00001
    old_bkg = ini*0.9999
    lamb = []
    for i in xrange(nimg):
#        snr = sig.wiener(abs(ratio).astype('float64'))#+finfo(type(ratio[0,0])).eps*1.e6
#        lamb += [(snr)**2.]# * 0. + _lambda]
#        lamb += [10.*abs(obji[i])/stddev[i]]
        ratio = abs(obji[i])/stddev[i]
        ratio /= median(ratio)
        ratio = minimum(ratio, 20.)
        ratio = sig.wiener(abs(ratio).astype('float64'), (5,5))
        lamb += [2.**(ratio)**1.]
#        lamb += [(abs(obji[i])/stddev[i])**6.]
#    lamb[0] *= 10.
#        lamb[i] = convol(r, lamb[i])
    
    
    ######## temp ##############
#    lamb[0] = sig.wiener(lamb[0])
#    lamb[0] *= (lamb[0]>1.)*10000.+1.
#    lamb[0][log10(lamb[0])<1.] /= 100.
#    lamb[0][log10(lamb[0])>1.] *= 0.1
#    ini = sig.wiener(abs(ini), (7,7))#.astype('float64'))
#    old_bkg = ini*0.9999
#    lamb[0] /= 100.
    if _lambda != 0. and _lambda is not None:
        lamb[0] = lamb[0]*0. + _lambda
#    psf[0] = r
    #############################
    
    
    def add_sources(srcpar, resi, img_nb):
#        for i in xrange(nb_src):
#            c1, c2, i0 =  srcpar[i*(2+nimg)], srcpar[i*(2+nimg)+1], srcpar[i*(2+nimg)+2+img_nb]
#            fl = i0*1.133*gres**2.
#            sources[img_nb].add_source(mpar[:4], gpar, gpos, gstrat,  [c1,c2,i0], fwhm0=gres, flux=fl)
#        olderr = ((resi - sources[img_nb].array)/sigmai)**2.
        err = []
        param = oldsrc.copy()
        sources[img_nb].reset()
        for i in xrange(len(srcpar)):
            param[i-1] = oldsrc[i-1]
            param[i] = srcpar[i]
            sources[img_nb].reset()
            for i in xrange(nb_src):
                c1, c2, i0 =   param[i*(2+nimg)], param[i*(2+nimg)+1], param[i*(2+nimg)+2+img_nb]
                fl = i0*1.133*gres**2.
                sources[img_nb].add_source(mpar[:4], gpar, gpos, gstrat, [c1,c2,i0], fwhm0=gres, flux=fl)
            err += [(((resi - sources[img_nb].array)/sigmai)**2.).sum()]  
        sources[img_nb].reset()
        for i in xrange(nb_src):
            c1, c2, i0 =  srcpar[i*(2+nimg)], srcpar[i*(2+nimg)+1], srcpar[i*(2+nimg)+2+img_nb]
            fl = i0*1.133*gres**2.
            sources[img_nb].add_source(mpar[:4], gpar, gpos, gstrat,  [c1,c2,i0], fwhm0=gres, flux=fl)
        return abs(array(err))#-olderr.sum())
    def add_sources2(srcpar, bkg, img_nb):
#        sources[img_nb].reset()
#        for i in xrange(nb_src):
#            c1, c2, i0 =  srcpar[i*(2+nimg)], srcpar[i*(2+nimg)+1], srcpar[i*(2+nimg)+2+img_nb]
#            sources[img_nb].addGaus_fnorm_trunc(gres, c1, c2, i0)
#        olderr = (((obji[img_nb] - convol(psf[img_nb], bkg + sources[img_nb].array))/sigmai[img_nb])**2.)
        err = []
        #get the old values back
        param = oldsrc.copy()
        #compute the error for each parameter
        for i in xrange(len(srcpar)):
            #change the parameter to evaluate
            param[i-1] = oldsrc[i-1]
            param[i] = srcpar[i]
            #set the model according to the parameters
            sources[img_nb].reset()
            for i in xrange(nb_src):
                c1, c2, i0 =  param[i*(2+nimg)], param[i*(2+nimg)+1], param[i*(2+nimg)+2+img_nb]
                sources[img_nb].addGaus_fnorm_trunc(gres, c1, c2, i0)
            #add the error of the ith parameter to the error list
#            err += [((fn.rebin(obj[img_nb] - fn.mean(convol(psf[img_nb], bkg + sources[img_nb].array),bshape[0],bshape[1]),sshape)*0.25/sigmai[img_nb])**2.).sum()]
            err += [(((obji[img_nb] - convol(psf[img_nb], bkg + sources[img_nb].array))/sigmai[img_nb])**2.).sum()]
        #set the model with the new parameters
        sources[img_nb].reset()
        for i in xrange(nb_src):
            c1, c2, i0 =  srcpar[i*(2+nimg)], srcpar[i*(2+nimg)+1], srcpar[i*(2+nimg)+2+img_nb]
            sources[img_nb].addGaus_fnorm_trunc(gres, c1, c2, i0)
        #return the error list 
        return abs(array(err))#-olderr.sum())
    def errfun_ana(bkgpar, srcpar):
        global TRACE, err
        bkg = bkgpar.reshape(sshape)
        smoothed = convol(r, bkg) 
        err.fill(0.)
        for i in xrange(len(psf)):
            conv = convol(psf[i], bkg) 
            resi = obji[i]-conv
            srcerr = add_sources(srcpar, resi, i)
            oldsrc = srcpar.copy()
            resi -= sources[i].array
            err += (resi/sigmai[i])**2. + lamb[i]*(bkg-smoothed)**2.
        TRACE += [err.sum()]
        return append(err.ravel(), srcerr)
    def errfun_num(bkgpar, par):
        global TRACE, err, old_bkg
        bkg = bkgpar.reshape(sshape)
        smoothed = convol(r, bkg) 
        err.fill(0.)
        srcerr = zeros(len(par))
        for i in xrange(len(psf)):
            srcerr += add_sources2(par, bkg, i)
            oldsrc = par.copy()
            resi = obji[i] - convol(psf[i], bkg + sources[i].array)
            err += lamb[i]*(resi/sigmai[i])**2.
#            err += filt.maximum_filter(resi/sigmai[i], gres//2*2+3)**2.
        err += (bkg-smoothed)**2.
#        no_neg_constr = bkg<0.
#        err *= (no_neg_constr)*10. + logical_not(no_neg_constr)
        TRACE += [err.sum()]
#        TRACE += [par[0]]#[err.sum()]
        return append(err.ravel(), srcerr)
    
#    errfun = errfun_ana
    errfun = errfun_num
    
    out(2, 'Starting the fit process')
    t0 = time.time()
    #########
    bpar = ini.copy()
    spar = srcini.copy()
#    shiftpar_ini[:2] = 0.
#    shiftpar_ini = array([0.31107003608294009, 0.040379029333831085, 0.48386989278418863, 0.29383536029606905, 0.35526840095850043, 0.24770074671464354])
    lambda_col = []
    resi_col = []
    obji_bk = deepcopy(obji)
    sigmai_bk = deepcopy(sigmai)
    def _shift(i, dx, dy):
        im = Image(obji_bk[i], noisemap=sigmai_bk[i])
        im.shiftToCenter(sshape[0]/2.+dx, sshape[1]/2.+dy, center_mode='O')
        return flux_o[i]*im.array/im.array.sum(), flux_s[i]*im.noiseMap/im.noiseMap.sum()
    def shift_err(params):
        if any(abs(params)>20.):
            return errfun(bpar, spar)**10.
        for i in xrange(nimg-1):
            dx, dy = params[2*i: 2*i+2]
            obji[i+1], sigmai[i+1] = _shift(i+1, dx,dy)
#            offsets[i] = params[2*i: 2*i+2]
        return errfun(bpar, spar)
    shift_col = []
#    lamb[0] *= 10000.
    for i in xrange(nbruns):
        out(2, 'Run', i+1, '/', nbruns)
        for j in xrange(nimg):
            obji[j] = obji_bk[j]*(trust_threshold + i/nbruns*(1.-trust_threshold))
            
#        npar, spar = alg.minimi( errfun2, npar.ravel(), spar, itnb=itnb*(i**1./20.+1), prec=0., 
        bpar, spar = alg.minimi( errfun, bpar.ravel(), spar, itnb=itnb, prec=0., 
                                 minstep_px=dev/100., maxpos_step=maxpos_step/(i+1), 
                                 max_iratio_step=max_iratio_step/(i+1), 
#                                 stepfact=stepfact*(i+1), nbsrc=nb_src, nbimg=nimg)[0]#*2.**(i))[0]
                                 stepfact=stepfact*10.**i, nbsrc=nb_src, nbimg=nimg)[0]#*2.**(i))[0]
        out(2)

        if (not i % max(nbruns//nbruns, 1) or i+1==nbruns) and nimg > 1:
#            if i == 1: lamb[0] /= 100.
            out(2, 'Correcting shift...', '-r')
            if i+1 == nbruns: 
                shiftpar = scipy.optimize.leastsq(shift_err, shiftpar_ini, maxfev = 30*nimg, warning=False)[0]
            else:
                shiftpar = scipy.optimize.leastsq(shift_err, shiftpar_ini, maxfev = 10*nimg, warning=False)[0]
            shift_err(shiftpar)
            shiftpar_ini = shiftpar
#            out(2, 'Correcting shift...',  'Done!', '-r')
#            out(2)
            out(2, 'Done!')
            shift_col += [shiftpar]
#        if i == 0: lamb[0] /= 10000.
    out(2, 'Done in', time.time()-t0, 'seconds')
    
    
    model = [bpar.reshape(sshape), array(spar)]
    
    out(2, 'Initial sources parameters [x,y,I]:', srcini)
    out(2, 'Final sources parameters [x,y,I]:', model[1]) 
#    out(2, 'Sources intensities:', [model[1][3+i] for i in xrange(nimg)])
    print 'offsets:', shift_col
#    print 'real:', ws.pick('offsets', 'true_par.dat')
    
    out(2, 'Writing the results...')
    errfun_num(model[0].ravel(), model[1])  
    fn.array2fits(model[0]+sources[0].array, 'results/deconv.fits')
    for i in xrange(nimg):
#        fn.array2fits((obj[i] - fn.mean(convol(psf[i], model[0]+sources[i].array), bshape[0], bshape[1]))/sigma[i], 
#                     'results/resi_'+str(i+1)+'.fits')
        fn.array2fits((obji[i] - convol(psf[i], model[0]+sources[i].array))/sigmai[i], 
                     'results/resi_'+str(i+1)+'.fits')
        fn.array2fits(sources[i].array, 'results/sources_'+str(i+1)+'.fits')
        fn.array2fits(obji[i], 'results/data_'+str(i+1)+'_interp.fits')
    fn.array2fits(model[0], 'results/bkg.fits')
    fn.array2fits(lamb[0], 'results/lambda.fits')
#    fn.array2fits(resi_col[z,i[0],i[1]], 'results/resi_opt.fits')
    
    ws.drop('found_par', model[1])
#    ws.drop('ini_par', srcini)
    if nimg > 1:
        ws.drop('offsets', shift_col[-1])
    else:
        ws.drop('offsets', [])
    
    
    if show is True:
        out(2, 'Displaying the results...')
        fn.array2ds9(model[0]+sources[0].array, frame = 1, name='model')
#        fn.array2ds9(toterr, frame = 3, name='resi')
        fn.array2ds9(sources[0].array, frame = 2, name='sources')
        fn.array2ds9(model[0], frame = 3, name='bkg')
        chi2 = errfun(model[0].ravel(), model[1])[:len(model[0].ravel())].reshape(sshape)
        fn.array2fits(chi2, 'results/chi2.fits')
        for i in xrange(nimg):
            fn.array2ds9(obj[i], frame = 4+i*2, name='obj')
#            fn.array2ds9(abs(obj[i] - fn.mean(convol(psf[i], model[0]+sources.array), bshape[0], bshape[1]))/sigma[i], 
            fn.array2ds9(fn.get_data('resi_'+str(i+1)+'.fits'), 
                         frame = 5+i*2, name='resi_'+str(i+1), zscale=True) 
            fn.array2ds9(lamb[i], frame = 6+i*2, name='lambda', zscale=True) 
#            fn.array2ds9((obji[i] - convol(psf[i], model[0]+sources[i].array))/sigmai[i], 
#                         frame = 6+i*2, name='resi_'+str(i+1))
#        fn.array2ds9(lmodel[0], frame = 7, name='lm')
#        fn.array2ds9(chi2, frame = 4, name='chi2')
        
        import pylab as p
        p.figure(1)
        trace = array(TRACE[:-2])
        X = arange(trace.shape[0])
        p.title('Error evolution')
        p.plot(X, trace)
        p.draw()
        p.savefig('results/trace%(fnb)02d.png'% {'fnb':1})
        p.show()
    if cuda:
        out(2, 'Freeing CUDA context...')
        context.pop()
    if nimg > 1:
        return model[1],  shift_col[-1], srcini
    return model[1],  [], srcini


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
    out(2, FILENAME)
    out(2, 'Restore data from extracted files')
    fnb = ws.get_filenb(FILENAME)
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


