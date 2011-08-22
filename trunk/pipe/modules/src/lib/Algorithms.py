        

__version__ = '0.3.5'
__date__ = '2009'
__author__ = "Cantale Nicolas - EPFL <n.cantale@gmail.com>"
        
        
        
from scipy import optimize
import sys
import utils as fn
#from utils import *
#from numpy import *
import numpy as np
from PSF import PSF
import AImage
         
out = fn.Verbose()
        
        
class GausAlg():
    """
    Class gathering the different methods and strategies used in the gaussian fit
    """
    def __init__(self, stars, sfact, npix, mpar, std_dev=0.):
        """
        Input: 
         - 
        """
        self.stars = stars
        self.sfact = sfact
        self.mpar = mpar
        self.npix = npix
        self.sdev = std_dev
        #center in small pixels:
        self.sc1    = npix*sfact/2.
        self.sc2    = npix*sfact/2.
        #center in big pixels:
        self.bc1    = npix/2.
        self.bc2    = npix/2.
        self.run_nb = 0
        self.psfs    = PSF((npix*sfact,npix*sfact), (npix*sfact/2.,npix*sfact/2.))
        if mpar is not None:
            self.pos = np.zeros((len(stars), 2))
            for  i, star in enumerate(stars):
                self.pos[i,0] = mpar.getCenter(i)[0]/sfact
                self.pos[i,1] = mpar.getCenter(i)[1]/sfact
        
    def fit(self, stars, params, strategy, fitrad):
        if strategy == 'grid':
            self.grid_fun(stars, params)
        elif strategy == '2grids':
            return self.twogrids_fun(stars, params)
        elif strategy == 'alternate' or strategy == 'weighted' or strategy == 'mixed':
            return self.pos_fun(strategy, stars, params, fitrad)
        else:
            raise ValueError, 'Unknown strategy: '+str(strategy)
            
    
    ############################### Algorithms #####################################
    
    def pos_fun(self, strat, stars, params, fitrad):
        """
        Due to their high similarities, those three strategies are gathered here. 
        """
        #import pdb
        #pdb.set_trace()
        median = None
        itnb, gnb, gsize, fwhmin = params
        bounds = None
        if strat == 'alternate':
            mainstar_id = self.run_nb % self.mcs.star_nb
            self.run_nb += 1
            if fitrad is not None:
                bounds = stars[mainstar_id].residuals.shape[0]/2., stars[mainstar_id].residuals.shape[1]/2.,fitrad
            gpos, gnb = fn.getGpos(stars[mainstar_id].residuals, gnb, gsize, bounds)
            c1, c2 = stars[mainstar_id].par.getLocpar(mainstar_id)[0:2]
            gpos[:,0] -= c1/self.sfact
            gpos[:,1] -= c2/self.sfact
        elif strat == 'weighted':
            median = self._getMedian(stars, noised=False, crop = False)[0]
            if fitrad is not None:
                bounds = median.shape[0]/2., median.shape[1]/2.,fitrad
            gpos, gnb = fn.getGpos(median, gnb, gsize, bounds)
            gpos[:,0] -= self.npix/2.
            gpos[:,1] -= self.npix/2.
        elif strat == 'mixed':
            gpos = np.array([])
            gnb_t = 0
            for star in stars:
                c1, c2 = star.par.getLocpar(star.id-1)[0:2]
                bounds = c1/star.sampling_factor, c2/star.sampling_factor, star.residuals.shape[0]/2
                if fitrad is not None:
                    bounds = c1/star.sampling_factor, c2/star.sampling_factor, fitrad
                g, n = fn.getGpos(star.residuals, gnb, gsize, bounds, gpos)
                g[:,0] -= int(c1/star.sampling_factor)
                g[:,1] -= int(c2/star.sampling_factor)
                gpos = np.append(gpos, g)
                gnb_t += n
            gnb = gnb_t
            gpos.shape = gpos.shape[0]/2, 2     
#        if gnb == 0:
#            return array([]), array([]), 0., PSF((self.npix*self.sfact, self.npix*self.sfact)), zeros((self.npix, self.npix))
        alg = MinAlg()
        for star in stars:
            star.setup_pos(gpos, fwhmin)
        par = []
        for p in gpos:
            if strat == 'weighted':
                #par += [median[p[0]+self.npix/2.,p[1]+self.npix/2.], 2.*fwhmin]
                par += [0.01, 2.*fwhmin]
            else:
                par += [0., 2*fwhmin]
        ################ mini ##################
        t = time.time()
        opar = alg.minimalize(self.pos_err, np.array(par), itnb)
        out(2)
        out(2, 'Done in:', time.time()-t, 's')
        res = np.array([])
        for star in self.stars:
            #star.gpos_eval(opar)
            star.build_diffg(opar)
            res = np.append(res,star.chig)
        final_errg = (res**2.).sum() / (self.npix**2 * len(self.stars))
        opar.shape = len(opar)/2,2 
#        print '[intensity', 'fwhm]'
#        print opar
        ########################################
        cnt = 0
        gausdistr = np.zeros((self.npix, self.npix))
        psfg = PSF((self.npix*self.sfact, self.npix*self.sfact),(self.npix*self.sfact/2., self.npix*self.sfact/2.))
        for g in gpos:
            psfg.addGaus_fnorm(opar[cnt,1], 
                               g[0]*self.sfact+self.sfact*self.npix/2., 
                               g[1]*self.sfact+self.sfact*self.npix/2., 
                               opar[cnt,0])
            gausdistr[g[0]+self.npix/2., g[1]+self.npix/2.]=1
            cnt += 1
        #psfg.normalize()
        return opar, gpos, final_errg, psfg, gausdistr
        
    def pos_err(self, params):
        res = np.array([])
        foreach(lambda i: self.stars[i].gpos_eval(params), np.arange(len(self.stars)), threads=(len(self.stars)))
        for star in self.stars:
            #star.gpos_eval(params)
            res = np.append(res, star.chig)
        err = (res**2.).sum() / (self.npix**2 * len(self.stars))
        out(2, "error: "+str(err)+"                 ", '-r')
        return res.ravel()
        
        
        
        
                   
    ###################################################################################
    def twogrids_fun(self, stars, params):
        #set the parameters
        itnb, smoothing, inner, idispersion, outer, odispersion = params
        alg = MinAlg()
        r = max(inner, outer)
        med = np.zeros((r, r))
        for star in self.stars:
            med += star.setup_ggridfit(params[1:])
        med = med/len(self.stars)
        par = []
        for i in xrange(0, int(inner), idispersion):
            for j in xrange(0, int(inner), idispersion):
                #parameters: intesity, fwhm
                par += [0.3*med[i,j]/max(abs(med.min()),med.max()), smoothing*2.]
                #par += [0.01, smoothing*5.]
        for i in xrange(0, int(outer), odispersion):
            for j in xrange(0, int(outer), odispersion):
                #parameters: intesity, fwhm
                par += [0.3*med[i,j]/max(abs(med.min()),med.max()), smoothing*2.]
                #par += [0.1, smoothing*2.]
        t = time.time()
        opar = alg.minimalize(self.grid_err, np.array(par), itnb)
        print '\nDone in:', time.time()-t, 's'
        res = np.array([])
        for star in self.stars:
            star.ggrid_eval(opar)
            res = np.append(res,star.chig)
            star.build_diffg()
        final_errg = (res**2.).sum() / (self.npix**2. * len(self.stars))
        opar.shape = len(opar)/2,2 
        c1, c2 = self.sc1, self.sc2
        psfg = PSF((self.npix*self.sfact, self.npix*self.sfact),(self.npix*self.sfact/2., self.npix*self.sfact/2.))
        cnt = 0
        if inner > 0:
            for i in xrange(int(c1 - inner/2), int(c1 + inner/2 + inner % 2), idispersion):
                for j in xrange(int(c2 - inner/2), int(c2 + inner/2 + inner % 2), idispersion):   
                    if opar[cnt,1] < smoothing:
                        print 'fault'
                    psfg.addGaus_fnorm(opar[cnt,1], i, j, opar[cnt,0])
                    cnt += 1
        if outer > 0:        
            for i in xrange(int(c1 - outer/2), int(c1 + outer/2 + outer%2), odispersion):
                for j in xrange(int(c2 - outer/2), int(c2 + outer/2 + outer%2), odispersion):   
                    if opar[cnt,1] < smoothing:
                        print 'fault'
                    psfg.addGaus_fnorm(opar[cnt,1], i, j, opar[cnt,0])
                    cnt += 1        
        return opar, np.array([]), final_errg, psfg
        
    def grid_err(self, params):
        res = np.array([])
        foreach(lambda i: self.stars[i].ggrid_eval(params), np.arange(len(self.stars)), 
                threads=len(self.stars))
        for star in self.stars:
            #star.ggrid_eval(params)
            res = np.append(res, star.chig)
        err = (res**2.).sum() / (self.npix**2. * len(self.stars))
        sys.stdout.write("\rError per pixel: "+str(err)+"           ")
        sys.stdout.flush()
        return res.ravel()
            
    ###################################################################################
    def grid_fun(self, stars, params):
        #set the parameters
        diameter, smoothing, itnb = params
        alg = MinAlg()
        med = np.zeros((diameter, diameter))
        for star in self.mcs.star_tab:
            med += star.setup_cgausfit(diameter, smoothing)
        med = med/self.mcs.star_nb
        par = []
        for i in xrange(int(diameter)):
            for j in xrange(int(diameter)):
                #parameters: intesity, fwhm
                #par += [med[i,j]/2., smoothing*2.]
                par += [0.1, smoothing*2.]
        t = time.time()
        opar = alg.minimalize(self.center_err, np.array(par), itnb)
        print '\nDone in:', time.time()-t, 's'
        res = np.array([])
        for star in self.mcs.star_tab:
            star.cgaus_eval(opar)
            res = np.append(res,star.chig)
        self.mcs.final_errg = (res**2.).sum() / (self.mcs.star_size * self.mcs.star_nb)
        opar.shape = len(opar)/2,2 
        print opar
        c1, c2, rad = self.mcs.sshape[0]/2., self.mcs.sshape[1]/2, diameter/2.
        cnt = -1
        for i in xrange(int(c1 - rad), int(c1 + rad)):
            for j in xrange(int(c2 - rad), int(c2 + rad)):
                cnt += 1                      
                self.mcs.psfg.addGaus_fnorm(opar[cnt,1], i, j, opar[cnt,0])
        
    def center_err(self, params):
        res = np.array([])
        foreach(lambda i: self.mcs.star_tab[i].cgaus_eval(params), np.arange(self.mcs.star_nb), threads=self.mcs.star_nb)
        for star in self.mcs.star_tab:
            #star.cgaus_eval(params)
            res = np.append(res, star.chig)
        err = (res**2.).sum() / (self.mcs.star_size * self.mcs.star_nb)
        sys.stdout.write("\rError per pixel: "+str(err))
        sys.stdout.flush()
        return res.ravel()
        
    ###################################################################################
    def alt_fun(self, stars, params):
        itnb, gnb, gsize, fwhmin = params
        mainstar_id = self.run_nb % self.mcs.star_nb
        self.run_nb += 1
        alg = MinAlg()
        gpos, gnb = self.getGpos(stars[mainstar_id].residuals, gnb, gsize)
        c1, c2 = stars[mainstar_id].par.getLocpar(mainstar_id)[0:2]
        gpos[:,0] -= c1/self.mcs.sampling_factor
        gpos[:,1] -= c2/self.mcs.sampling_factor
        
        
    ############################# Basic functions ###################################
    def _gaus(self, c1, c2, i0, fwhm, fwhm0 = 0.):
        sig = (fwhm / (2. * np.sqrt(2.*np.log(2.))))**2. + (fwhm0 / (2. * np.sqrt(2.*np.log(2.))))**2.
        g = lambda x,y: i0*np.exp((-(x-c1)**2. - (y-c2)**2)/(2.*sig))
        return np.fromfunction(g, self.sshape)
        
    def _getMedian(self, stars, noised = True, crop = True):
        res = np.zeros(stars[0].image.array.shape)
        cross_noise = np.zeros(stars[0].image.array.shape)
        for  i, star in enumerate(stars):
            if noised == True:
                noise = AImage.Image(star.image.noiseMap).shiftToCenter(self.pos[i,0], self.pos[i,1], 
                                                                           interp_order=3, center_mode='O', 
                                                                           ret=True).copy()
            else:
                noise = 1.
            res += AImage.Image(star.residuals).shiftToCenter(self.pos[i,0], self.pos[i,1], 
                                                                 interp_order=3, center_mode='O',
                                                                 ret = True) / noise
            cross_noise += 1. / noise
        if crop == True:
            radius = self.radius
            res = res[res.shape[0]/2.-radius : res.shape[0]/2.+radius , res.shape[1]/2.-radius : res.shape[1]/2.+radius].copy()
            cross_noise = cross_noise[res.shape[0]/2.- radius : res.shape[0]/2.+radius, res.shape[1]/2.-radius : res.shape[1]/2.+radius].copy()
        return res / len(stars), cross_noise
    
    def _getMom(self, img):
        total = img.sum()
        X, Y = np.indices(img.shape)
        c1 = (X*img).sum()/total
        c2 = (Y*img).sum()/total
        col = img[:, int(c2)]
        width_x = np.sqrt(abs(((np.arange(col.size)-c2)**2*col).sum()/col.sum()))
        row = img[int(c1), :]
        width_y = np.sqrt(abs(((np.arange(row.size)-c1)**2*row).sum()/row.sum()))
        I = img[c1,c2]
        return [c1, c2, I, width_x, width_y]
    
    def _mean(self, a, *args):
        '''rebin ndarray data into a smaller ndarray of the same rank whose dimensions
        are factors of the original dimensions. eg. An array with 6 columns and 4 rows
        can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
        example usages:
        >>> a=rand(6,4); b=rebin(a,3,2)
        >>> a=rand(6); b=rebin(a,2)
        '''
        shape = a.shape
        lenShape = len(shape)
        factor = np.asarray(shape)/np.asarray(args)
        evList = ['a.reshape('] + \
                 ['args[%d],factor[%d],'%(i,i) for i in xrange(lenShape)] + \
                 [')'] + ['.sum(%d)'%(i+1) for i in xrange(lenShape)] + \
                 ['/factor[%d]'%i for i in xrange(lenShape)]
        return eval(''.join(evList))
    
        
        
        
class MinAlg():
    """
    Wrapper around the various python methods for minimalization
    """
    def __init__(self, type=None):
        if type == None or type == 'leastsq':
            self.type = 'leastsq'
        elif type == 'bfgs':
            self.type = 'bfgs'
        elif type == 'anneal':
            self.type = 'anneal'
        elif type == 'cg':
            self.type = 'cg'
        elif type == 'powell':
            self.type = 'powell'
        elif type == 'simplex':
            self.type = 'simplex'
        elif type == 'brute':
            self.type = 'brute'
        else:
            raise ValueError, 'Incorrect MinAlg type'
    
    def minimalize(self, f, x, it_nb=0, dfun=None):
        #import time
        #t=time.time()
        
        if it_nb == -1:
            f(x)
            return x 
        elif self.type == 'leastsq':
            return self._leasq(f, x, it_nb, dfun = dfun)
        elif self.type == 'bfgs':
            return self._bfgs(f, x, it_nb, dfun = dfun)
        elif self.type == 'anneal':
            return self._anneal(f, x, it_nb)
        elif self.type == 'cg':
            return self._cg(f, x, it_nb, dfun = dfun)
        elif self.type == 'powell':
            return self._powell(f, x, it_nb, dfun = dfun)
        elif self.type == 'simplex':
            return self._simplex(f, x, it_nb, dfun = dfun)
        elif self.type == 'brute':
            return self._brute(f, x, maxit=it_nb)
        
        #print time.time()-t
        
    def _leasq(self, f, x, it_nb = 0, dfun=None):
        """
        Uses the Levenberg-Marquandt algorithm.
        """
        params, s = optimize.leastsq(f, x, maxfev = it_nb, warning=False)#, factor=0.1, diag=(1.,0.2,0.1,0.2,1.,1.,0.1,1.,1.,0.1,1.,1.,0.1))#, Dfun = dfun, col_deriv=1)
        return params
        
    def _bfgs(self, f, x, it_nb = 0, dfun=None):
        """
        Function minimalization using the BFGS algorithm
        """
        #the lambda function transform the array of chi2 values to a single value
        #necessary for the fmin_bfgs function
        params = optimize.fmin_bfgs(lambda x: (f(x)**2).sum(), x, maxiter = it_nb, fprime=dfun)
        return params
    
    def _simplex(self, f, x, it_nb = 0, dfun=None):
        """
        Uses the Nelder-Mead simplex algorithm.
        """
        params, s = optimize.fmin(lambda x: (f(x)**2).sum(), x, maxiter = it_nb)
        return params
    
    def _anneal(self, f, x, it_nb):
        """
        Function minimalization using simulated annealing
        """
        params = optimize.anneal(lambda x: (f(x)**2).sum(), x, maxiter=it_nb)
        return params
    
    
    def _cg(self, f, x, it_nb, dfun=None):
        """
        Function minimalization using a nonlinear conjugate gradient algorithm
        """
        #TODO: control if the function should be quadratic near the minimum (twice differenciable)
        params = optimize.fmin_cg(lambda x: (f(x)**2).sum(), x, maxiter=it_nb)
        return params
    
    def _powell(self, f, x, it_nb, dfun=None):
        """
        Function minimalization using simulated annealing
        """
        params = optimize.fmin_powell(lambda x: (f(x)**2).sum(), x, maxiter=it_nb)
        return params
    
    def _brute(self, f, x, maxit = 0):
        """
        Function minimalization using brute force
        """
        old = (f(x))**2
        min, max = 0., 1. #old.min(), old.max()
        median = (max+min)/2.
        dir = np.zeros(x.shape)
        step = np.zeros(x.shape)
        param = x.copy()
        """
        if maxit == -1:
            maxit = 1
        elif maxit == 0:
            maxit = 2000
        """
        it = 0
        for i in xrange(x.shape[0]):
            if x[i] < median:
                step[i]= (max-median)/5.
            else:
                step[i]= -(median-min)/5.
        while it < maxit:
            param += step
            new = (f(param))**2
            for i in xrange(x.shape[0]):
                if old[i] < new[i]:
                    step[i] = -step[i]/2.
            old = new.copy()
            it += 1
        return param
    
import time
import threading
from itertools import izip, count

def foreach(f,l,threads=3,return_=False):
    """
    Apply f to each element of l, in parallel
    """

    if threads>1:
        iteratorlock = threading.Lock()
        exceptions = []
        if return_:
            n = 0
            d = {}
            i = izip(count(),l.__iter__())
        else:
            i = l.__iter__()


        def runall():
            while True:
                iteratorlock.acquire()
                try:
                    try:
                        if exceptions:
                            return
                        v = i.next()
                    finally:
                        iteratorlock.release()
                except StopIteration:
                    return
                try:
                    if return_:
                        n,x = v
                        d[n] = f(x)
                    else:
                        f(v)
                except:
                    e = sys.exc_info()
                    iteratorlock.acquire()
                    try:
                        exceptions.append(e)
                    finally:
                        iteratorlock.release()
        
        threadlist = [threading.Thread(target=runall) for j in xrange(threads)]
        for t in threadlist:
            t.start()
        for t in threadlist:
            t.join()
        if exceptions:
            a, b, c = exceptions[0]
            raise a, b, c
        if return_:
            r = d.items()
            r.sort()
            return [v for (n,v) in r]
    else:
        if return_:
            return [f(v) for v in l]
        else:
            for v in l:
                f(v)
            return

def parallel_map(f,l,threads=3):
    return foreach(f,l,threads=threads,return_=True)



def minimi_full(func, param, srcpar, itnb=0, prec=0., stddev=None, maxpos_step=0.5, 
               max_iratio_step=0.02, stepfact=1.):
    if prec <= 0.:
        prec = 1e-15
    par = np.append(param, srcpar)
    srclen = len(srcpar)
    if srclen == 0: srclen = -len(param)
    err = func(param, srcpar)
    olderr = err*2.
    epsilon = err.sum() / err.shape[0]**2.
    neweps = epsilon-2.*prec
    dir = np.sign(olderr-err)
    actives = np.zeros(err.shape)
    minierr = epsilon
    minipar = par.copy()
    if stddev is None: stddev = param.std()
    #1st solution
#    maxstep = (abs(par)/float(stddev) + 1.)*stddev
    #2nd solution
#    dev=zeros(par.shape)+stddev/10.
#    maxstep = maximum(dev, abs(par))
    #3rd solution
    maxstep = abs(par)
    
    maxstep /= stepfact
    step = maxstep / 5.
    l = len(param)
    if  l > 0:
        for i in xrange(len(srcpar)//3):
            maxstep[l+i*3:l+i*3+2] = maxpos_step#par[l+i*3:l+i*3+2]/100.
            step[l+i*3:l+i*3+2] = maxpos_step/5.
            maxstep[l+i*3+2] = par[l+i*3+2]*max_iratio_step
            step[l+i*3:l+i*3+2] = maxstep[l+i*3+2]
    space = 1
    for i in xrange(actives.shape[0]/space):
        actives[i*space] = 1.
    i = 0
    while i < itnb:
        newdir = -(actives-1)*dir + actives*np.sign(err)
        changedir = np.sign(abs(olderr) - abs(err))
        newstep = changedir*step*((changedir+1)*0.6 + (-changedir+1)/4.)
        newstep = np.sign(newstep)*np.minimum(abs(newstep), maxstep)
        step = -(actives-1)*step + actives*newstep
        dir = newdir.copy() 
        newpar = par + actives*step
        olderr = -(actives-1)*olderr + actives*err
        if not i % 1:
            actives[:-1] = actives[1:]
            actives[-1] = actives[0]
        err = func(newpar[:-srclen], newpar[-srclen:])
        neweps = err.sum() / err.shape[0]**2.
        if epsilon < neweps and not any(changedir>0):# or abs(epsilon-neweps) < prec:
            out(2)
            out(2, 'Stop conditions met, exiting...')
            break
        par = newpar.copy()
        epsilon = neweps
        if epsilon < minierr:
            minierr = epsilon
            minipar = par.copy()
        out(2, int(((i+1.)/itnb)*100.), '% done.', 'Error:', epsilon, '-r')
        i += 1
    return [minipar[:-srclen], minipar[-srclen:]], [par[:-srclen], par[-srclen:]]

def minimi(func, param, srcpar, itnb=0, prec=None, minstep_px=None, maxstep_px=None, maxpos_step=0.5, 
               max_iratio_step=0.02, stepfact=None, nbsrc=0, nbimg=1):
    import waveletdenoise
    if prec <= None:
        prec = 0.#1e-15
    par = np.append(param, srcpar)
    srclen = len(srcpar)
    if srclen == 0: srclen = -len(param)
    err = func(param, srcpar)
    olderr = err*2.
    epsilon = err.sum() / err.shape[0]**2.
#    neweps = epsilon-2.*prec
    dir = np.sign(olderr-err)
    minierr = epsilon
    minipar = par.copy()
    if minstep_px is None: minstep_px = param.std()/100.
    if maxstep_px is None: maxstep = np.maximum(abs(par)/10., param.std())
    else: maxstep = np.zeros(par.shape) + maxstep_px
    if stepfact is None: stepfact = 1.
    
    maxstep /= stepfact
    minstep = np.zeros(maxstep.shape) + minstep_px/stepfact
    maxstep = np.maximum(maxstep, minstep)
    step = maxstep.copy()
    l = len(param)
    if  l > 0:
        if nbsrc == 0: nbsrc = len(srcpar)//3
        for i in xrange(nbsrc):        
            maxstep[l+i*(2+nbimg):l+i*(2+nbimg)+2] = maxpos_step#par[l+i*3:l+i*3+2]/100.
            minstep[l+i*(2+nbimg):l+i*(2+nbimg)+2] = maxpos_step/100.#par[l+i*3:l+i*3+2]/100.
            step[l+i*(2+nbimg):l+i*(2+nbimg)+2] = maxpos_step/5.
            for j in xrange(nbimg):
                maxstep[l+i*(2+nbimg)+2+j] = par[l+i*(2+nbimg)+2+j]*max_iratio_step
                minstep[l+i*(2+nbimg)+2+j] = par[l+i*(2+nbimg)+2+j]*max_iratio_step/1000.
                step[l+i*(2+nbimg)+2+j] = maxstep[l+i*(2+nbimg)+2+j]
#            maxstep[l+i*3:l+i*3+2] = maxpos_step#par[l+i*3:l+i*3+2]/100.
#            step[l+i*3:l+i*3+2] = maxpos_step/5.
#            maxstep[l+i*3+2] = par[l+i*3+2]*max_iratio_step
#            step[l+i*3:l+i*3+2] = maxstep[l+i*3+2]
    hist = [i for i in xrange(10)]
    hist_mean = [i for i in xrange(10)]
    i = best_it = 0
    while i < itnb:
        try:
##################################
#            err, resi = func(par[:-srclen], par[-srclen:], ret_all=True)
#            direction = np.sign(abs(olderr) - abs(err))
#            step = direction*step*((direction+1)*0.55 + (-direction+1)/4.) #if no change: *2*nb1 else *-2/nb2
#            step = np.sign(step)*np.clip(np.abs(step), minstep, maxstep)
#            step[:-srclen] = waveletdenoise.cyclespin(resi, 3, 0.003).ravel()/10.
#            par += step
#            epsilon = err.sum() / err.shape[0]**2.
#            hist = hist[1:] + [epsilon]
#            hist_mean = hist_mean[1:] + [np.mean(hist)]
#            olderr = err.copy()
##################################

            direction = np.sign(abs(olderr) - abs(err))
            step = direction*step*((direction+1)*0.55 + (-direction+1)/4.) #if no change: *2*nb1 else *-2/nb2
            step = np.sign(step)*np.clip(np.abs(step), minstep, maxstep)
            newpar = par + step
            olderr = err.copy()
            err = func(newpar[:-srclen], newpar[-srclen:])
            hist = hist[:-1] + [epsilon]
            hist_mean = hist_mean[:-1] + [np.mean(hist)]
            epsilon = err.sum() / err.shape[0]**2.
##################################
            
#            if abs(epsilon-neweps) < prec:# or abs(epsilon-neweps) < prec:
            if np.abs(hist_mean[0]-hist_mean[-1]) < hist_mean[-1]/10. and False:
                out(3)
                out(3, 'Stop conditions met, exiting...')
                break
            par = newpar.copy()
            if epsilon < minierr:
                minierr = epsilon
                minipar = par.copy()
                best_it = i
            out(3, int(100*(i+1.)/itnb), '% done.', 'Error:', epsilon, '-r')
            i += 1
        except KeyboardInterrupt:
            break
    out(3)
    out(3, 'Best parameters at iteration', best_it+1)
    return [minipar[:-srclen], minipar[-srclen:]], [par[:-srclen], par[-srclen:]]


def minimi_num(func, param, itnb=0, prec=0., stddev=None, stepfact=1.):
    out(2, 'Begin minimization')
    if prec <= 0.:
        prec = 1e-15
    par = param.copy()
    err = func(param)
    olderr = err*2.
    epsilon = err.sum() / err.shape[0]**2.
    neweps = epsilon-2.*prec
    dir = np.sign(olderr-err)
    actives = np.zeros(err.shape)
    minierr = epsilon
    minipar = par.copy()
    if stddev is None: stddev = param.std()
    maxstep = (abs(par)//stddev + 1.)*stddev
    maxstep /= stepfact
    step = maxstep / 5.
    space = 1
    for i in xrange(actives.shape[0]/space):
        actives[i*space] = 1.
    i = 0
    while i < itnb:
        newdir = -(actives-1)*dir + actives*np.sign(err)
        changedir = np.sign(abs(olderr) - abs(err))
        newstep = changedir*step*((changedir+1)*0.6 + (-changedir+1)/4.)
        newstep = np.sign(newstep)*np.minimum(abs(newstep), maxstep)
        step = -(actives-1)*step + actives*newstep
        dir = newdir.copy() 
        newpar = par + actives*step
        olderr = -(actives-1)*olderr + actives*err
        if not i % 1:
            actives[:-1] = actives[1:]
            actives[-1] = actives[0]
        err = func(newpar)
        neweps = err.sum() / err.shape[0]**2.
        if epsilon < neweps and not any(changedir>0):# or abs(epsilon-neweps) < prec:
            out(2)
            out(2, 'Stop conditions met, exiting...')
            break
        par = newpar.copy()
        epsilon = neweps
        if epsilon < minierr:
            minierr = epsilon
            minipar = par.copy()
        out(2, int(((i+1.)/itnb)*100.), '% done.', 'Error:', epsilon, '-r')
        i += 1
    return minipar, par



def minimi_deriv(func, param, maxstep=None, itnb=0, prec=None):
    #TODO: assert types
    if prec <= None:
        prec = 0.#1e-15
#    par = append(param, srcpar)
    par = param.copy()
    srclen = len(par)
    l = len(param)
    err = func(par)
    olderr = err.copy()
    epsilon = err.sum() / err.shape[0]**2.
    neweps = epsilon-2.*prec
    dir = np.sign(olderr-err)
    minierr = epsilon
    minipar = par.copy()
    if maxstep is None: 
        maxstep = abs(par)
    step = maxstep / 5.
    i = 0
    while i < itnb:
        changedir = np.sign(abs(olderr) - abs(err))
        step = changedir*step*((changedir+1)*0.6 + (-changedir+1)/4.)
        step = np.sign(step)*np.minimum(abs(step), maxstep)
        newpar = par + step
        olderr = err.copy()
        err = func(newpar[:-srclen], newpar[-srclen:])
        neweps = err.sum() / err.shape[0]**2.
        if abs(epsilon-neweps) < prec:# or abs(epsilon-neweps) < prec:
            out(2)
            out(2, 'Stop conditions met, exiting...')
            break
        par = newpar.copy()
        epsilon = neweps
        if epsilon < minierr:
            minierr = epsilon
            minipar = par.copy()
        out(2, int(100*(i+1.)/itnb), '% done.', 'Error:', epsilon, '-r')
        i += 1
    return [minipar[:-srclen], minipar[-srclen:]], [par[:-srclen], par[-srclen:]]



def _mini(fun, params, args, minsteps, maxsteps):
    pass

        



        
        
    
    
        
        
        
        
