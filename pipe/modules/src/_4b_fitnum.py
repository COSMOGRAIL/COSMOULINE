#!/usr/bin/python

from src.lib.AImage import Image
from src.lib.Star import Star
from src.lib.Param import Param
from src.lib.waveletdenoise import cyclespin
#from src.lib.Algorithms import *
from src.lib.deconv import Dec, DecCLEAN, DecMC, DecWL, DecML
import src.lib.utils as fn
import src.lib.wsutils as ws
import numpy as np
import copy, sys
out = fn.Verbose()

def fitnum(fit_id, data, params, savedir = 'results/', liveplot=False):
    starpos, npix, sfactor, mpar = params['STARS'], params['NPIX'], params['S_FACT'], copy.deepcopy(params['MOF_PARAMS'])
    gres, fitrad, psf_size, itnb =  params['G_RES'], params['FIT_RAD'], params['PSF_SIZE'], params['MAX_IT_N']
    nbruns, show, _lambda, stepfact = params['NB_RUNS'], params['SHOW'], params['LAMBDA_NUM'], params['BKG_STEP_RATIO_NUM']
    cuda, radius, stddev, objsize = params['CUDA'], params['PSF_RAD'], params['SIGMA_SKY'], params['OBJ_SIZE']
    minstep, maxstep, thresh = params['MIN_STEP_NUM'], params['MAX_STEP_NUM'], params['WL_THRESHOLD_NUM']

    stars = []
    mofpar = Param(1, 0)
    bshape = data['stars'][fit_id][0].shape
    sshape = (int(bshape[0]*sfactor), int(bshape[1]*sfactor))

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
    else:
        conv = fn.conv
        cuda = False
    r /= r.sum()
    
    ############### Set the smoothing ###############
    _lambda = fn.get_lambda(sshape, radius+5., _lambda)
    sm = r.copy()
#    if not thresh:
#        thresh = params['SIGMA_SKY']
    ############## Initializations ##############
    for i, pos in enumerate(starpos):           
            #populates the stars array:
            im = Image(copy.deepcopy(data['stars'][fit_id][i]), 
                       noisemap = copy.deepcopy(data['sigs'][fit_id][i]), 
                       mask = copy.deepcopy(data['masks'][fit_id][i])) 
#            im.shiftToCenter(mpar[fit_id][4+3*i]/sfactor,mpar[fit_id][4+3*i+1]/sfactor, center_mode='O')
#            mpar[fit_id][4+3*i:4+3*i+2] = sshape[0]/2., sshape[1]/2. 
            stars += [Star(i+1, im, mofpar, sfactor, gres, False)]
    mofpar.fromArray(np.array(mpar[fit_id]), i = -1)
    img_shifts = []
    mof_err = 0.
    for i, s in enumerate(stars):
        s.moff_eval()
        s.build_diffm()
        s.image.noiseMap /= mpar[fit_id][6+3*i]
        s.diffm.array /= mpar[fit_id][6+3*i]
        img_shifts += [((mpar[fit_id][4+3*i]-r_len/2.), (mpar[fit_id][5+3*i]-r_len/2.))]
        mof_err += (np.logical_not(s.image.mask)*abs(s.diffm.array/s.image.noiseMap)).sum()
    
    ############ Deconvolution ############
#    dec = DecCLEAN([s.diffm.array for s in stars],
#    dec = DecMC([s.diffm.array for s in stars],
#    dec = DecWL([s.diffm.array for s in stars],
#    dec = DecML([s.diffm.array for s in stars],
    dec = Dec([s.diffm.array for s in stars], 
              [s.image.noiseMap for s in stars], 
              [s.image.mask for s in stars], 
              r, sm, conv, img_shifts, _lambda, gres, thresh)
#    bak = dec.deconv()
    dec.ini *= fn.get_circ_mask_exp(dec.ini.shape, radius)
    bak = dec.deconv(itnb, minstep, maxstep, stepfact, radius)
#    bak = cyclespin(bak, 3, dec._get_dn_threshold(bak)[0]*10.)
    bak_conv = conv(r, bak)
    bak *= fn.get_circ_mask_exp(bak.shape, radius)#, exp=4.)
    ##########
    gaus_err = 0.
    for i, im in enumerate(stars):           
        gaus_err += abs(dec.get_im_resi(bak_conv, i)).sum()
    out(2, "indicative error gain:", 100*(1. - gaus_err/mof_err), "%")  

    ########## Set the numerical PSF ##########
    out(2, 'Building the final PSF...')
    if psf_size is None:
        psf_size = objsize
    size = psf_size*sfactor, psf_size*sfactor
    psf, s = fn.psf_gen(size, bak, mpar[fit_id][:4], [[]], [[]], 'mixed', sfactor)
    
    ############ Prepare output ############
    imgs, names = [], []
    imgs += [psf.array, s, bak, dec.ini]
    names += ['psf_'+str(fit_id+1), 's_'+str(fit_id+1), 'psf_num_'+str(fit_id+1), 'psfnum_ini_'+str(fit_id+1)]
    for i, s in enumerate(stars):           
        resi = dec.get_im_resi(bak_conv, i, ret_all=True)[1]
        imgs += [s.diffm.array, resi]
        names += ["difmof%(fnb)02d_%(n)02d" % {'fnb':fit_id+1, 'n': s.id}, 
                  "difnum%(fnb)02d_%(n)02d" % {'fnb':fit_id+1, 'n': s.id}]
            
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
    p.figure()
    trace = np.array(dec.trace)
    X = np.arange(trace.shape[0])
    p.title('Error evolution')
    p.plot(X, trace)
#    p.legend()
    p.draw()
    p.savefig(savedir+'trace_fitnum%(fnb)02d.png'% {'fnb':fit_id+1})
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
        from . import prepare
        prepare.main(['_3_fitmof.py', '-ce', cfg])
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    out(1, 'Begin background fit')
    PSF_SIZE = None
    SHOW = False
    f = open(cfg, 'r')
    exec(f.read())
    f.close()
    vars = ['FILENAME', 'SHOW', 'STARS','NPIX', 'MOF_PARAMS', 
            'G_PARAMS', 'G_POS', 'G_STRAT', 'S_FACT', 'NOWRITE', 
            'G_RES', 'CENTER', 'IMG_GAIN', 'SIGMA_SKY',
            'SKY_BACKGROUND', 'G_SETTINGS', 'NB_RUNS', 'FIT_RAD']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        return 1
    out(2, 'Restore data from extracted files')
    files, cat = ws.get_files(FILENAME, 'img') #@UndefinedVariable
    fnb = len(cat)
    data = ws.restore(*ws.getfilenames(fnb))
    data['filenb'] = fnb
    data['starnb'] = len(STARS) #@UndefinedVariable
    gpar = []
    gpos = []
    for i in range(fnb):
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

    
