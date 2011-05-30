#!/usr/bin/python

import sys, pylab, scipy.stats.mstats, scipy.optimize
import numpy as np
import src.lib.utils as fn
import src.lib.wsutils as ws

out = fn.Verbose()

def get_sky_val(data, show=False, range=None, nbins=None, save=None):
    #TODO: prendre la median a partir d'un certain point
    if range is None: range = [0.01,0.99]
    d = data.copy() 
    d[np.where(np.isnan(d))] = np.median(data)
    q = scipy.stats.mstats.mquantiles(d.ravel(), prob=[0, range[0], range[1], 1])
    if nbins is None: 
        nbins = np.max(100, int(np.abs(q[1])+np.abs(q[2])))
    out(2, 'Building histogram...')
    h = np.histogram(d.ravel(), bins = np.linspace(q[1],q[2],nbins), normed=False)
    out(2, 'Done: ', repr(nbins), "bins, ", "median =", repr(np.median(d)))
    out(2, 'Begin gaussian fit...')
    bnind = np.where(h[0]==h[0].max())[0][0]
    g = lambda c, f, I: lambda x: I*np.exp(-(x-c)**2/(2*f**2))
    errfun = lambda p: g(*p)(h[1][:h[0].shape[0]]) - h[0]
    print (h[1][bnind], np.abs(h[1][-1]-h[1][0])/20., h[0][bnind])
    p, success = scipy.optimize.leastsq(errfun, 
                                        (h[1][bnind], np.abs(h[1][-1]-h[1][0])/20., h[0][bnind]), 
#                                        (h[1][bnind], h[0].shape[0]/20., h[0][bnind]), #changed for hst, get back if needed
#                                        maxfev=1000, 
                                        warning=False)
    p[1] = np.abs(p[1])
    out(2, 'Done!')
    out(2, "fit results: center (sky) =", repr(p[0]), "FWHM =", repr(p[1]), "intensity =", repr(p[2]))
    pylab.figure(1)
    pylab.plot(h[1][:h[0].shape[0]], h[0], label='data distribution')
    pylab.plot(h[1][:h[0].shape[0]], errfun(p)+h[0], label='gaussian fit')
    pylab.plot(h[1][:h[0].shape[0]], errfun(p), label='error')
    pylab.legend()
    if show == True:
        pylab.show()
    if save != None:
        pylab.savefig(save)
    pylab.clf()
    return p[0], p[1]
    

def main(argv=None):
    cfg = 'config.py'
    if argv is not None:
        sys.argv = argv
    opt, args = fn.get_args(sys.argv)
    if args is not None: cfg = args[0]
    p = False
    SKY_RANGE = NBINS = SHOW = None
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME', 'NOWRITE']
    err = fn.check_namespace(vars, locals())
    if 's' in opt: 
        out.level = 0
    if 'v' in opt: 
        out.level = 2
    if 'd' in opt: 
        DEBUG = True
        out.level = 3
        out(1, '~~~ DEBUG MODE ~~~')
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    if 'p' in opt:
        sky, sig = get_sky_val(fn.get_data(args[0], directory='.'), show = True, range=SKY_RANGE, nbins=NBINS)
        out(1, 'Analysis done! Sky:', sky, 'sigma:', sig)
        return 0
    if err > 0:
        return 1
    out(2, FILENAME, cfg) #@UndefinedVariable
    files, cat = ws.get_files(FILENAME, directory='images') #@UndefinedVariable
    skyl = []
    sigl = []
    fnb = len(files)
    for i in xrange(fnb):
        out(1, '===============', i+1, '/', fnb,'===============|')
        out(1, 'Getting sky from', files[i])
        sky, sig = get_sky_val(fn.get_data(files[i], directory='images'), show = SHOW, range=SKY_RANGE, nbins=NBINS)
        skyl += [sky]
        sigl += [sig]
        out(1, 'Analysis done! Sky:', sky, 'sigma:', sig)
    out(1, '------------------------------------------')
    out(1, 'sky:', skyl, 'sigma:', sigl)
    if NOWRITE is False and not p: #@UndefinedVariable
        fn.write_cfg(cfg, {'SKY_BACKGROUND':skyl, 'SIGMA_SKY':sigl})
    return 0
    
    
if __name__ == "__main__":
    sys.exit(main())
