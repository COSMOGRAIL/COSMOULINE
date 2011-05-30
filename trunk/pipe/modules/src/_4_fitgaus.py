#!/usr/bin/python


from src.lib.AImage import *
from src.lib.Star import *
from src.lib.Param import *
from src.lib.Algorithms import *
import src.lib.utils as fn
import src.lib.wsutils as ws
from numpy import *

out = fn.Verbose()

PAR = Param(1, 0)
STAR_COL = []

def __errFun(params):
    """
    Error function for the moffat fit. Builds all PSFs with the given settings
    Input: parameters of the Moffat given in an array: [theta, width, ell, beta] + [c1, c2, i0]*
    Output: array with the chi square values of the PSFs 
    """
    global PAR
    global STAR_COL
    global TRACE
    PAR.fromArray(params, i = 0)
    TRACE += [params]
    result = array([])
    #uses multi-threading:
    foreach(lambda i: STAR_COL[i].moff_eval(), arange(len(STAR_COL)), threads=len(STAR_COL))
    for star in STAR_COL:
        #star.moff_eval()
        result = append(result, star.chi)
    
    #err = (result**2).sum()/(STAR_COL[0].image.array.shape[0]**2*len(STAR_COL))
    #sys.stdout.write("\rError: "+ str(err)+"           ")
    #sys.stdout.flush()
    #print "Error per pixel:", err
    return ravel(result)

def fitgaus(fit_id, data, params, savedir = 'results/'):
    starpos, npix, sfactor, mpar = params['STARS'], params['NPIX'], params['S_FACT'], params['MOF_PARAMS']
    g_res, gstrat, gpar, fitrad = params['G_RES'], params['G_STRAT'], params['G_SETTINGS'], params['FIT_RAD']
    nbruns, show, psf_size = params['NB_RUNS'], params['SHOW'], params['PSF_SIZE']
    global PAR
    global STAR_COL
    PAR = Param(1, 0)
    STAR_COL = []
    gaus = PSF((npix*sfactor, npix*sfactor),
                (npix*sfactor/2.-1., npix*sfactor/2.-1.))
    psf = PSF((npix*sfactor, npix*sfactor),
              (npix*sfactor/2.-1., npix*sfactor/2.-1.))
    mofpar = Param(1, 0)
    for i, pos in enumerate(starpos):           
            #populates the stars array:
            im = Image(data['stars'][fit_id][i], noisemap = data['sigs'][fit_id][i])    
            STAR_COL += [Star(i+1, im, mofpar, sfactor, g_res, False)]
    mofpar.fromArray(array(mpar[fit_id]), i = -1)
    for s in STAR_COL:
        s.moff_eval()
        s.build_diffm()
    alg = GausAlg(STAR_COL, sfactor, npix, mofpar)
    mof_err = 0.
    for star in STAR_COL:
        mof_err += abs(star.diffm.array).sum()
    gparl, gposl = [], []
    final_errg = 0.
    old = final_errg
    joker = 2
    fini = gpar[3]
    for i in range(nbruns):
        out(2, "run nb", i+1)
        if i>0 and gstrat != "grid" and gstrat != "2grid" and False:
            fnew = gpar[3]*0.6
            if fnew >= fini: 
                gpar = gpar[:3] + [fnew]
            else:
                gpar[3] *= 3.
        par, pos, final_errg, psfg, gd = alg.fit(STAR_COL, gpar, gstrat, fitrad)
        gaus.array += psfg.array
        #TODO: add correctly!!!
        psf.array += psfg.array
        gparl += [par.tolist()]
        gposl += [(sfactor*pos).tolist()]
        #export(self)
        if i>0 and final_errg >= old:
            out(2, "warning, increasing error: +", final_errg - old)
            joker -= 1
            if joker < 1:
                out(2, "no remaining joker, exiting")
                break
            out(2, "remaining jokers:", joker)
        else:
            joker = 2
            old = final_errg
        print '-----------------------------------------------------'
    #for star in self.star_tab:
    #    star.build_diffg()
    gaus_err = 0.
    for star in STAR_COL:
        gaus_err += abs(star.diffg.array).sum()
    out(2, "indicative error gain:", 100*(1. - gaus_err/mof_err), "%")  
    
    
    mof = PSF((npix*sfactor, npix*sfactor), (npix*sfactor/2., npix*sfactor/2.))
    mof.setMof(append(mpar[fit_id][0:4], array([npix*sfactor/2., npix*sfactor/2., 1.])),  fwhm0 = 0.)
    psf = PSF((npix*sfactor, npix*sfactor))
    psf.set_finalPSF(mpar[fit_id][0:4], gparl, gposl, gstrat)
    mof.normalize()
    gaus.normalize()
    imof = Image(mof.array)
    igaus = Image(gaus.array)
    for s in STAR_COL:
        s.diffg.writetofits("results/difg%(n)02d.fits" % {'n': s.id})
    if show == True:
        #imof.showds9(ds9frame=1,imgname="Moffat")
        igaus.showds9(ds9frame=1,imgname="Gaussians")
        #fn.array2ds9(psfs.array, frame=3, name="PSF")
        array2ds9(STAR_COL[0].psfg.array,frame=2, name='gaus_conv')
        array2ds9(gd,frame=3, name='gaus_distr')
        i = 4
        for s in STAR_COL:
            #s.image.showds9(ds9frame=i,imgname="star"+str(i/2))
            s.diffm.showds9(ds9frame=i,imgname="diffm_"+str(s.id))
            s.diffg.showds9(ds9frame=i+1,imgname=   "diffg_"+str(s.id))
            i += 2
    if savedir is not None:
        for s in STAR_COL:
            s.diffm.writetofits(savedir+"difm%(n)02d.fits" % {'n': s.id})
            s.diffg.writetofits(savedir+"difg%(n)02d.fits" % {'n': s.id})
        Image(gaus.array).writetofits(savedir+"psfg.fits")
#        Image(gaus.array+mof.array).writetopng(savedir+"psfs.png")
#        Image(gaus.array+mof.array).writetofits(savedir+"psfs.fits")
        Image(psf.array).writetofits(savedir+"psf_1.fits")
        Image(STAR_COL[0].psfg.array).writetofits(savedir+"psfg_conv.fits")
    return gparl, gposl
    
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
    out(1, 'Begin gaussian fit')
    SHOW = None
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME', 'STARS','NPIX', 'MOF_PARAMS', 
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
    for i in xrange(fnb):
        out(1, '===============', i+1, '/', fnb,'===============')
        out(1, 'Working on', files[i])
        
        gauspar, gauspos = fitgaus(i, data, locals())
        gpar += [gauspar]
        gpos += [gauspos]
    out(1, '------------------------------------------')
    out(1, 'Gaussian fit done')
    if NOWRITE is False: #@UndefinedVariable
        fn.write_cfg(cfg, {'G_PARAMS':gpar, 'G_POS':gpos})
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

    
