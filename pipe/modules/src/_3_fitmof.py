#!/usr/bin/python

from src.lib.AImage import Image
from src.lib.Star import Star
from src.lib.Param import Param
from src.lib.Algorithms import *
import src.lib.wsutils as ws
import src.lib.utils as fn
from numpy import *
import time, numpy

out = fn.Verbose()

PAR = Param(1, 0)
it = 0
TRACE = []
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
    global it
    it += 1
    PAR.fromArray(params, i = 0)
    TRACE += [params.copy()]
    result = array([])
    #uses multi-threading:
    foreach(lambda i: STAR_COL[i].moff_eval(), arange(len(STAR_COL)), threads=len(STAR_COL))
    for star in STAR_COL:
        #star.moff_eval()
        result = append(result, star.chi)
    err = (result**2).sum()/(STAR_COL[0].image.array.shape[0]**2*len(STAR_COL))
#    sys.stdout.write("\rError: "+ str(err)+"           ")
#    sys.stdout.flush()
    out(2, 'Error:', err, '-r')
    return result.ravel()

def fitmof(fit_id, data, params, savedir='results/'):
    global PAR
    global STAR_COL
    global TRACE
    global it
    PAR = Param(1, 0)
    it = 0
    TRACE = []
    STAR_COL = []
    starpos, npix, g_res = params['STARS'], params['NPIX'], params['G_RES']
    it_nb, show, sfactor = params['MAX_IT'], params['SHOW'], params['S_FACT']
    mofini = params['MOF_INIT']
    mof = PSF((npix*sfactor, npix*sfactor), (npix*sfactor/2., npix*sfactor/2.))
    for i, pos in enumerate(starpos):           
            #populates the stars array:
            im = Image(data['stars'][fit_id][i].copy(), noisemap = data['sigs'][fit_id][i].copy(), 
                       mask = data['masks'][fit_id][i].copy())    
            STAR_COL += [Star(i+1, im, PAR, sfactor, g_res, False)]
    if mofini is not None: 
        PAR.setMofpar(0,mofini)
    opt_params = PAR.toArray()
    if any(isnan(opt_params)):
        if any(isnan(opt_params[4:])):
            out(2, 'Stuck during parameters approximation: aborted fit', fit_id+1)
            out(2, opt_params)
            return opt_params, []
        out(2, 'Stuck during parameters approximation: Trying default values...')
        opt_params[0:4] = 0.1, 4., 0.1, 2.

    algo = MinAlg()
    out(2, "Running Moffat fit...")
    t = time.time()
    opt_params = algo.minimalize(__errFun, opt_params, it_nb = it_nb)
    opt_params[0] = opt_params[0]%(2.*pi)
    opt_params[1] = numpy.abs(opt_params[1])
    PAR.setOptpar(*opt_params)
    out(2)
    out(2, "Done in", time.time()-t, "[s] and", it, "iterations. Optimal parameters:")
    out(2, " theta:", opt_params[0], " FWHM:", opt_params[1], " e:", opt_params[2], " beta:", opt_params[3])
    for star in STAR_COL:
        star.moff_eval()
        star.build_diffm()
    #compute the final error
    result = array([])
    for star in STAR_COL:
        result = append(result, star.chi)
    out(2, 'Final error:', (result**2).sum()/(npix**2.*len(STAR_COL)))
    #create the final PSF
    c1, c2 = mof.array.shape
    c1 = c1/2.
    c2 = c2/2.
    mof.addMof_fnorm(append(PAR.getMofpar(0), array([c1,c2, 1.])),  fwhm0 = 0.)
    mof.array /= mof.array.sum()
    imof = Image(mof.array)
    if savedir is not None:
        for s in STAR_COL:
            s.diffm.writetofits(savedir+"difmof%(fnb)02d_%(n)02d.fits" % {'fnb':fit_id+1, 'n': s.id})
        imof.writetofits(savedir+"psfm%(fnb)02d.fits"% {'fnb':fit_id+1})
    if show == True:
        Image(mof.array).showds9(ds9frame=1,imgname="Moffat")
        i = 2
        for s in STAR_COL:
            s.image.showds9(ds9frame=i,imgname="star"+str(i/2))
            s.diffm.showds9(ds9frame=i+1,imgname="diffm"+str(i/2))
            i += 2
            
    if show == True:
        import pylab as p
        p.figure(1)
        trace = array(TRACE)
        X = arange(trace.shape[0])
        for i in xrange(4):
            p.subplot(2,2,i+1)
            p.title(['theta','width','e','beta'][i])
            p.plot(X, trace[:,i])
        p.show()
        if savedir is not None:
            p.savefig(savedir+'trace%(fnb)02d.png'% {'fnb':fit_id+1})
    #return the optimal parameters of the moffat
    return PAR.toArray(), [Image(mof.array),STAR_COL]

def main(argv=None):
#    cfg = base+str(i+1)+'.py'
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
    out(1, 'Begin moffat characterization')
    
    MOF_INIT = None
    MAX_IT = 0
    SHOW = False
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME', 'NOWRITE', 'STARS','NPIX', 'S_FACT', 
            'G_RES', 'IMG_GAIN', 'SIGMA_SKY', 'SKY_BACKGROUND']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        out(3, 'Error in file', cfg)
        return 1
    
    out(2, 'Restore data from extracted files')
    files, cat = ws.get_files(FILENAME, 'img') #@UndefinedVariable
    fnb = len(cat)
    data = ws.restore(*ws.getfilenames(fnb))
    data['filenb'] = fnb
    data['starnb'] = len(STARS) #@UndefinedVariable
    out(1, 'Begin moffat fit on', FILENAME) #@UndefinedVariable
    mpar = []
    for i in xrange(fnb):
        out(1, '===============', i+1, '/', fnb,'===============')
        out(1, 'Working on', files[i])
        mofpar, r = fitmof(i, data, locals())
        mpar += [mofpar.tolist()]
    out(1, '------------------------------------------')
    out(1, 'Moffat fit done')
    if NOWRITE is False: #@UndefinedVariable
        fn.write_cfg(cfg, {'MOF_PARAMS':mpar})
    return 0
    
    
if __name__ == "__main__":
#    import cProfile, pstats
#    prof = cProfile.Profile()
#    prof = prof.runctx("main()", globals(), locals())
#    stats = pstats.Stats(prof)
#    stats.sort_stats("time")  # Or cumulative
#    stats.print_stats(15)  # how many to print
    sys.exit(main())

    
