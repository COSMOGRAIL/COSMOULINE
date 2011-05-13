#!/usr/bin/python


from lib.AImage import *
from lib.Star import *
from lib.Param import *
from lib.Algorithms import *
import lib.utils as fn
import lib.wsutils as ws
import numpy as np
import scipy.ndimage.interpolation, copy

out = fn.Verbose()

PAR = Param(1, 0)
STAR_COL = []
TRACE = []

def paste_psf(psf, dest, pos, val):
#    crop_x1 = (x-rad)*((x-rad)>0)
#    crop_x2 = (size-1)*((x+rad)>=size) + (x+rad)*((x+rad)<size)
#    crop_y1 = (y-rad)*((y-rad)>0)
#    crop_y2 = (size-1)*((y+rad)>=size) + (y+rad)*((y+rad)<size)
    x, y = pos
    size = psf.shape[0]
    rad = size/2.
    cr_x1 = max(x-rad, 0)
    cr_x2 = min(x+rad, size)
    cr_y1 = max(y-rad, 0)
    cr_y2 = min(y+rad, size)
    r_x1 = max(rad-x, 0)
    r_x2 = min(rad+size-x, size)
    r_y1 = max(rad-y, 0)
    r_y2 = min(rad+size-y, size)
    dest[cr_x1:cr_x2, cr_y1:cr_y2] += psf[r_x1:r_x2, r_y1:r_y2]*val
    
def fitnum(fit_id, data, params, savedir = 'results/'):
    global PAR
    global STAR_COL
    global TRACE
    
    starpos, npix, sfactor, mpar = params['STARS'], params['NPIX'], params['S_FACT'], copy.deepcopy(params['MOF_PARAMS'])
    gres, fitrad, psf_size, itnb =  params['G_RES'], params['FIT_RAD'], params['PSF_SIZE'], params['MAX_IT_N']
    nbruns, show, lamb, stepfact = params['NB_RUNS'], params['SHOW'], params['LAMBDA_NUM'], params['BKG_STEP_RATIO_NUM']
    cuda, radius, stddev, objsize = params['CUDA'], params['PSF_RAD'], params['SIGMA_SKY'], params['OBJ_SIZE']
    center = params['CENTER']

    PAR = Param(1, 0)
    STAR_COL = []
    TRACE = []
    mofpar = Param(1, 0)
    bshape = data['stars'][fit_id][0].shape
    sshape = (int(bshape[0]*sfactor), int(bshape[1]*sfactor))

    r_len = sshape[0]
    c1, c2 =  r_len/2., r_len/2.
    center = 'SW'
    if cuda and fn.has_cuda():
        out(2, 'CUDA initializations')
        center = 'SW'
        context, plan = fn.cuda_init(sshape)
        r = fn.gaussian((r_len, r_len), gres, c1, c2, 1.)
        r = fn.switch_psf_shape(r, center)
        def conv(a, b):
            return fn.cuda_conv(plan, a, b)
    else:
        center = 'NE'
        nx = ny = r_len
        if center == 'O':
            c1, c2 = nx/2.-0.5, ny/2.-0.5
        elif center == 'NE':
            c1, c2 = nx/2., ny/2.
        elif center == 'SW':
            c1, c2 = nx/2.-1., ny/2.-1.
        conv = fn.conv
        r = fn.gaussian((r_len, r_len), gres, c1, c2, 1.)
        cuda = False
    r /= r.sum()
    
    for i, pos in enumerate(starpos):           
            #populates the stars array:
            im = Image(copy.deepcopy(data['stars'][fit_id][i]), noisemap = copy.deepcopy(data['sigs'][fit_id][i])) 
            STAR_COL += [Star(i+1, im, mofpar, sfactor, gres, False)]
    mofpar.fromArray(array(mpar[fit_id]), i = -1)
    mof_err = 0.
    
    rc1, rc2 = sshape[0]/2., sshape[1]/2.
    c = lambda x,y: (x-rc1)**2. + (y-rc2)**2. > radius**2.
    mask = fromfunction(c, sshape)
    lamb = mask*lamb/500. + (np.invert(mask))*lamb
    
    ini = array([])
    for i, s in enumerate(STAR_COL):
        s.moff_eval()
        s.build_diffm()
        s.image.noiseMap /= mpar[fit_id][6+3*(s.id-1)]
        s.diffm.array /= mpar[fit_id][6+3*(s.id-1)]
        #TODO: shift to center!!
        im = Image(s.diffm.array) 
        im.shiftToCenter(mpar[fit_id][4+3*i]/sfactor,mpar[fit_id][4+3*i+1]/sfactor, center_mode='O')
        ini = append(ini, fn.rebin(im.array, sshape)/sfactor**2.)
        mof_err += abs(s.diffm.array).sum()
    ini = median(ini.reshape((len(STAR_COL),sshape[0]*sshape[1])), 0)
    
    def get_err(bkg):
        param = bkg.reshape(sshape)
        err = zeros(sshape, dtype=float64)
        for i, s in enumerate(STAR_COL):           
            bk = Image(param) 
            bk.shiftToCenter(2.*c1-mpar[fit_id][4+3*i],2.*c2-mpar[fit_id][4+3*i+1], 
                             interp_order = 1, center_mode='O', mode='reflect')
            convo_m = fn.mean(bk.array, bshape[0], bshape[1])
            resi = (s.diffm.array - convo_m)/s.image.noiseMap
            dif = Image(resi) 
            dif.array = fn.rebin(dif.array, sshape)/sfactor**2.
            dif.shiftToCenter(mpar[fit_id][4+3*i],mpar[fit_id][4+3*i+1], 
                              interp_order = 1, center_mode='O', mode='reflect')
            err += dif.array
        return err
    
    def _mini(ini, it_nb):
        global TRACE
        model = np.copy(ini.reshape(sshape))*0.
        nstars = len(STAR_COL)
        err = get_err(model)
        chi2 = (err**2.).sum()/nstars**2.
        last_chi2 = chi2
        last_pos = -1,-1
        last_dir = -2
        last_err = np.copy(err)*0.99
        convo = zeros(sshape, dtype=float64)
        pos = np.unravel_index((np.invert(mask)*np.abs(err)).argmax(), err.shape)
        step = err[pos]/nstars/sfactor**2./r.max() /1000.#tmp!!!
#        step = np.median(err)/10.
        rr = fn.gaussian(sshape, gres, c1, c2, 1., 2.)
        rr /= r.sum()
        for i in xrange(it_nb):#*sshape[0]**2):
            pos = np.unravel_index((np.invert(mask)*np.abs(err)).argmax(), err.shape)
#            dir = np.sign(last_err[pos]-err[pos])
            dir = np.sign(err[pos])
            if pos == last_pos: 
                if dir==last_dir:
                    step *= 2.
                else:
                    step /= 4.
            else:
                step = err[pos]/nstars/sfactor**2./r.max() /1000.#tmp!!!
            step = min(step, 0.1)
            step = max(step, 0.001)
            last_dir = dir
            last_err = np.copy(err)
            last_pos = pos
            last_chi2 = chi2
#            dir = np.sign(err[pos])
#            step *= dir
            model[pos] += step*dir
            paste_psf(rr, convo, pos, step*dir)
            err = get_err(convo)
            chi2 = (err**2.).sum()/nstars**2.
            TRACE += [chi2]
#            print chi2, step, dir, model[pos], err[pos], dir
            out(3, 'Iteration', i, '- Changed pos:', pos, '- Error:', chi2, '-r')
#            out(3, 'Iteration', i, '- Changed pos:', pos, '- Dir:', dir, 'Step:',step, '- Error:', chi2, 'err',err[pos], '-r')
#            if chi2 > last_chi2:
#                out(3)
#                out(3, 'Increased error, exiting') 
#                break
        else:
            out(3)
        convo = conv(r, model)
        fn.array2ds9(err, frame=7)
        return convo, model
        
    out(2, 'Begin minimization procedure')
    t = time.time()
    
    npar = ini.copy()
    for i in xrange(nbruns):
        bak, high_freq = _mini(npar, 1500)#itnb//nbruns)
#        bak = _mini(npar, 1600)[1]#itnb//nbruns)
    out(2, 'Done in', time.time()-t,'[s]')
    
    convo = conv(r, bak)
    gaus_err = convo*0.
    for s in STAR_COL:
        gaus_err += fn.rebin(abs(s.diffm.array - fn.mean(convo, bshape[0], bshape[1])), sshape)/sfactor**2.
    gaus_err = gaus_err.sum()
    out(2, "indicative error gain:", 100*(1. - TRACE[-1]/TRACE[0]), "%")#gaus_err/mof_err), "%")  

    out(2, 'Building the final PSF...')
    #TODO: use the center option!!
    
    if psf_size is None:
        psf_size = objsize
    size = psf_size*sfactor, psf_size*sfactor
    psf, s = fn.psf_gen(size, bak, mpar[fit_id][:4], [[]], [[]], 'mixed', center, sfactor)
    
    if savedir is not None:
        out(2, 'Writing PSF to disk...')
        Image(s).writetofits(savedir+"s_"+str(fit_id+1)+".fits")
        Image(psf.array).writetofits(savedir+"psf_"+str(fit_id+1)+".fits")
        fn.array2fits(bak, savedir+'psfnum.fits')
        for i, s in enumerate(STAR_COL):           
            bk = Image(bak) 
            bk.shiftToCenter(2.*c1-mpar[fit_id][4+3*i],2.*c2-mpar[fit_id][4+3*i+1], interp_order = 1, center_mode='O')
            convo = conv(r, bk.array)
            convo_m = fn.mean(convo, bshape[0], bshape[1])
            resi = (s.diffm.array - convo_m)/s.image.noiseMap
#            resi = (s.diffm.array-fn.mean(conv(r,bak), bshape[0], bshape[1]))/s.image.noiseMap
            fn.array2fits(resi, savedir+"difnum%(n)02d.fits" % {'n': s.id})
    if show == True:
        out(2, 'Displaying results...')
        fn.array2ds9(psf.array, name='psf')
        fn.array2ds9(bak, name='psfnum', frame=2)
        i = 3
        for j, s in enumerate(STAR_COL):           
            s.diffm.showds9(ds9frame=i,imgname="difm_"+str(s.id))
            bk = Image(bak) 
            bk.shiftToCenter(2.*c1-mpar[fit_id][4+3*j],2.*c2-mpar[fit_id][4+3*j+1], interp_order = 1, center_mode='O')
            convo = conv(r, bk.array)
            convo_m = fn.mean(convo, bshape[0], bshape[1])
            resi = (s.diffm.array - convo_m)/s.image.noiseMap
            fn.array2ds9(resi, frame=i+1, name="resi_"+str(s.id))
            i += 2
    import pylab as p
    p.figure(1)
    trace = array(TRACE)
    X = arange(trace.shape[0])
    p.title('Error evolution')
    p.plot(X, trace)
    p.draw()
    if show == True:
        p.show()
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

    
