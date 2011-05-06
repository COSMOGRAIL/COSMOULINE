#!/usr/bin/python


from lib.AImage import *
from lib.Star import *
from lib.Param import *
from lib.Algorithms import *
from lib.deconv import *
import lib.utils as fn
import lib.wsutils as ws
import numpy as np
import copy

out = fn.Verbose()

def lambda_mask(shape, radius, val):
    rc1, rc2 = shape[0]/2., shape[1]/2.
    c = lambda x,y: ((x-rc1)**2. + (y-rc2)**2.) < radius**2.
    mask = fromfunction(c, shape)
    return np.invert(mask)*val*10000000. + mask*val

def fitnum(fit_id, data, params, savedir = 'results/'):
    starpos, npix, sfactor, mpar = params['STARS'], params['NPIX'], params['S_FACT'], copy.deepcopy(params['MOF_PARAMS'])
    gres, fitrad, psf_size, itnb =  params['G_RES'], params['FIT_RAD'], params['PSF_SIZE'], params['MAX_IT_N']
    nbruns, show, lamb, stepfact = params['NB_RUNS'], params['SHOW'], params['LAMBDA_NUM'], params['BKG_STEP_RATIO_NUM']
    cuda, radius, stddev, objsize = params['CUDA'], params['PSF_RAD'], params['SIGMA_SKY'], params['OBJ_SIZE']
    minstep, minstep = params['MIN_STEP_NUM'], params['MAX_STEP_NUM']

    stars = []
    mofpar = Param(1, 0)
    bshape = data['stars'][fit_id][0].shape
    sshape = (int(bshape[0]*sfactor), int(bshape[1]*sfactor))

    r_len = sshape[0]
    c1, c2 =  r_len/2., r_len/2.
    r = fn.gaussian(sshape, gres, c1, c2, 1.)
#    r = fn.LG_filter(sshape, gres, c1, c2)
    if cuda and fn.has_cuda():
        out(2, 'CUDA initializations')
        context, plan = fn.cuda_init(sshape)
        r = fn.switch_psf_shape(r, 'SW')
        def conv(a, b):
            return fn.cuda_conv(plan, a, b)
    else:
        conv = fn.conv
        cuda = False
    r /= r.sum()
    
    for i, pos in enumerate(starpos):           
            #populates the stars array:
            im = Image(copy.deepcopy(data['stars'][fit_id][i]), 
                       noisemap = copy.deepcopy(data['sigs'][fit_id][i])) 
#            im.shiftToCenter(mpar[fit_id][4+3*i]/sfactor,mpar[fit_id][4+3*i+1]/sfactor, center_mode='O')
#            mpar[fit_id][4+3*i:4+3*i+2] = sshape[0]/2., sshape[1]/2. 
            stars += [Star(i+1, im, mofpar, sfactor, gres, False)]
    mofpar.fromArray(array(mpar[fit_id]), i = -1)
    img_shifts = []
    mof_err = 0.
    for i, s in enumerate(stars):
        s.moff_eval()
        s.build_diffm()
        s.image.noiseMap /= mpar[fit_id][6+3*(s.id-1)]
        s.diffm.array /= mpar[fit_id][6+3*(s.id-1)]
        img_shifts += [((mpar[fit_id][4+3*i]-r_len/2.), (mpar[fit_id][4+3*i+1]-r_len/2.))]
        mof_err += abs(s.diffm.array/s.image.noiseMap).sum()
        
    lamb = lambda_mask(sshape, radius, lamb)
    
#    dec = DecPaste([s.diffm.array for s in stars],
#    dec = DecMC([s.diffm.array for s in stars],
    dec = Dec([s.diffm.array for s in stars], 
              [s.image.noiseMap for s in stars], 
              r, r, conv, img_shifts, lamb, gres)
    dec.deconv(itnb, minstep, minstep, stepfact, radius = radius)
    bak = dec.model
    
    gaus_err = 0.
    for i, im in enumerate(stars):           
        gaus_err += abs(dec.get_im_resi(bak, i)).sum()
    out(2, "indicative error gain:", 100*(1. - gaus_err/mof_err), "%")  

    out(2, 'Building the final PSF...')
    if psf_size is None:
        psf_size = objsize
    size = psf_size*sfactor, psf_size*sfactor
    psf, s = fn.psf_gen(size, dec.model, mpar[fit_id][:4], [[]], [[]], 'mixed', sfactor)
    
    imgs, names = [], []
    imgs += [psf.array, bak, dec.ini]
    names += ['psf', 'psf_num', 'psfn_ini']
    for i, s in enumerate(stars):           
        resi = dec.get_im_resi(bak, i)
        imgs += [s.diffm.array, resi]
        names += ["difmof%(n)02d" % {'n': s.id}, 
                  "difnum%(n)02d" % {'n': s.id}]
            
    if savedir is not None:
        out(2, 'Writing to disk...')
        for i, im in enumerate(imgs):
            fn.array2fits(im, savedir+names[i]+'.fits')
        fn.save_img(imgs, names, savedir+'overview.png', min_size=(256,256))
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
    p.savefig(savedir+'trace%(fnb)02d.png'% {'fnb':fit_id+1})
    if show == True:
        p.show()

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

    
