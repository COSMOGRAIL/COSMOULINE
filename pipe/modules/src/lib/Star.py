

__version__ = '0.3.5'
__date__ = '2009'
__author__ = "Cantale Nicolas - EPFL <n.cantale@gmail.com>"


from AImage import Image
from PSF   import PSF
import numpy as np
from scipy import signal
#from Scientific.Functions.FirstDerivatives import *



class Star():
    
    def __init__(self, id, image, param, sampling_factor, final_fwhm, nm_mod, use_mom=False):
        """
        Class containing all necessary information for the different 
        evaluations of the fitting methods. Implemented as yet: moffat
        evaluation, gaussian evaluation (grid, centered, positioned).
        Use this class by calling the eventual setup method, then the 
        desired evaluation method and finally the corresponding build_diff
        method.
        Input:
        - id              : ID of the class. Corresponds to its position
                            in the parameter arrays
        - image           : the image of the star (from class AstrImage)
        - param           : instance of the Param class, should common to 
                            all Star instances  
        - sampling_factor : small to big pixel ratio
        - final_fwhm      : the final resolution the star should attain 
        """   
        self.id                 = id
        self.image              = image
        self.sampling_factor    = sampling_factor
        self.wr                 = final_fwhm
        self.par                = param
        self.nm_mod             = nm_mod
        #width and height in small pixels:
        self.width              = float(self.image.array.shape[0]*self.sampling_factor)
        self.height             = float(self.image.array.shape[1]*self.sampling_factor)
        #shape of the image in big and small pixels:
        self.bshape             = self.image.array.shape
        self.sshape             = (int(round(self.width)), int(round(self.height)))
        #the different PSFs:
        self.psfm                = PSF(self.sshape, (self.width/2., self.height/2.))
        self.psfg               = PSF(self.sshape, (self.width/2., self.height/2.))
        self.psft               = PSF(self.sshape, (self.width/2., self.height/2.))
        self.psfnum             = PSF(self.sshape, (self.width/2., self.height/2.))
        #the end residuals of each method:
        self.diffm              = Image(np.zeros(self.bshape  , dtype = np.float64))
        self.diffg              = Image(np.zeros(self.bshape  , dtype = np.float64))
        self.diffnum            = Image(np.zeros(self.bshape  , dtype = np.float64))
        #the errors of each method:
        self.chi                = np.zeros(self.bshape, dtype = np.float64)
        self.chig               = np.zeros(self.bshape, dtype = np.float64)
        self.chinum             = np.zeros(self.bshape, dtype = np.float64)
        #copy of the residuals, used to allow iterative use of the gaussian technique  
        self.residuals          = np.zeros(self.bshape, dtype = np.float64)
        #gaussian used in an eventual convolution
        self._gaussian          = np.fromfunction(self._gaus(0, 2, 0, self.width/2.-1, self.height/2.-1, 1),
                                              self.sshape)
        self._gaussian          *= 1./self._gaussian.sum()
        #set the initial moffat parameters:
        if use_mom is True:
            self._preset() #uses only the moments
        else:
            self._preset() #more elaborated, uses the moments and a gaussian fit
    ############################### Moffat fit ##############################
    def moff_eval(self):
        """
        Evaluation of the moffat parameters contained in the Param instance given 
        at the initialization. Be sure these parameters are correctly updated before
        calling this function
        """
        self.psfm.setMof(np.append(self.par.getMofpar(0), self.par.getLocpar(self.id-1)), fwhm0 = self.wr)
        means = self._mean(self.psfm.array, self.bshape[0], self.bshape[1])
        self.chi = (np.logical_not(self.image.mask))*(self.image.array - means)/self.image.noiseMap
        
    def build_diffm(self):
        """
        Fill the diffm array and prepare the different table for the gaussian fit,
        including a modification of the noise map (adding weight to central pixels) 
        """
        self.diffm.array = self.image.array - self._mean(self.psfm.array, self.bshape[0], self.bshape[1])
        self.residuals = self.diffm.array.copy()
        if self.nm_mod == True:
            c1, c2, i0 = self.par.getLocpar(self.id-1)
            c1, c2 = c1/self.sampling_factor, c2/self.sampling_factor
            sum = abs(self.image.noiseMap).max()
            #the distant pixels should have less value:
            self.image.noiseMap *= np.fromfunction(lambda x,y: np.sqrt((x-c1)**2.+(y-c2)**2.)+1, self.bshape)
            sum2 = abs(self.image.noiseMap).max()
            self.image.noiseMap *= sum/sum2
            
    ##########################################################################
    

    ############################# gaussian fit ###############################    
    ##########################################################################
    def build_diffg(self, opar):
        """
        Fill the diffg array and prepare the different tables for the numerical fit or
        another gaussian iteration
        """
        self.gpos_eval(opar)
        self.psfg.array[:] = self.psft.array
        self.residuals -= self._mean(self.psfg.array, self.bshape[0], self.bshape[1])
        self.diffg.array[:] = self.residuals
        self.diffnum.array[:] = self.diffg.array
        
    ########################### Positioned gaussians algo #########################
    def setup_pos(self, gpos, fwhmin):
        """
        prepare the parameters for the gaussian fit
        Inputs:
        - gpos:   positions of the different gaussians, given as an array
                  containing the offsets of each gaussian according to the
                  image center
        - fwhmin: the minimal fwhm that the gaussians will be allowed to have
                  (not including the fwhm coming from the convolution)
        """
        self.gpos, self.fwhmin = gpos*self.sampling_factor, fwhmin
        
    def gpos_eval(self, params):
        """
        set gaussians according to the pre-defined positions.
        Input:
        - params: array with the intensity and fwhm for each gaussian 
        """
        #set the params to a friendlier shape
        par = np.array(params).reshape(params.shape[0]/2, 2)
        #get the mof center and base intensity
        c1, c2, i0 = self.par.getLocpar(self.id-1)
        self.psft.array[:] = self.psfg.array
#        p = PSFg(self.psft.array.shape)
#        if p.set_psf(c1, c2, self.gpos, i0*par[:,0], par[:,1], fwhm0=0., fwhmin=0.):
#            self.chig *= 1000000000
#        else:
#            self.chig = (self.residuals - self._mean(p.array, self.bshape[0], self.bshape[1]))/self.image.noiseMap
        cnt = 0
        fault = False
        for g in self.gpos:
            #check if the condition is observed
            if par[cnt,1] < self.fwhmin:
                fault = True             
                break       
            #two possible method for the gaussian evaluation: the second uses a cropped gaussian
#            self.psft.addGaus_fnorm(par[cnt,1], g[0]+c1, 
#                                    g[1]+c2, i0*par[cnt,0], self.wr)
            self.psft.addGaus_fnorm_trunc(par[cnt,1], g[0]+c1, 
                                          g[1]+c2, i0*par[cnt,0], self.wr)
            #uncomment the following if you want to display the gaussians positions on the diffm image:
            #self.diffm.array[g[0]+int(c1/self.sampling_factor), g[1]+int(c2/self.sampling_factor)] = 10000
            cnt += 1  
        if fault == True:
            #if the condition wasn't observed (it's the easiest way to set bounds to the leastsq algorithm):
            self.chig *= 1000000000
        else:
            #self.psft.normalize(i0)
            #the usual error function:
            self.chig = (self.residuals - self._mean(self.psft.array, self.bshape[0], self.bshape[1]))/self.image.noiseMap
    ############################################################################
    
    ########################## Gauss grid algorithm ##########################
    def setup_ggridfit(self, gparam):
        """
        prepare the parameters for the gaussian fit
        Inputs:
        - gparam: array or list containing:
            - fwhmin: the minimal fwhm that the gaussians will be allowed to have
                      (not including the fwhm coming from the convolution)
            - inrad:  the radius of the inner square 
            - idisp:  the space between two gaussian in the inner square
            - outrad: the radius of the outer square 
            - odisp:  the space between two gaussian in the outer square
        Output: returns an array of the size of the outer square containing
                the corresponding diffm values. (useful for the median computation)
        """
        self.residuals = self.diffm.array.copy()
        self.fwhmin, self.inrad, self.idisp, self.outrad, self.odisp = gparam
        self.isuppix = self.inrad%2
        self.osuppix = self.outrad%2
        self.inrad, self.outrad = self.inrad/2, self.outrad/2
        #get the max radius (in case the inner is bigger than the outer)
        if self.inrad > self.outrad:
            r = self.inrad
            sup = self.isuppix
        else:
            r = self.outrad
            sup = self.osuppix
        c1, c2, i0 = self.par.getLocpar(self.id-1)
        c1, c2 = int(c1/self.sampling_factor),int(c2/self.sampling_factor)
        #check for an eventual overstepping of the image border 
        if c1 - r < 0. or c2 - r < 0. or c1 + r >= self.bshape[0]  or c2 + r >= self.bshape[1]:
            raise ValueError, 'Bad gaussian fit diameter: too wide (' +  str(r)+ ' pixels)'
        return self.residuals[int(c1 - r) : int(c1 + r + sup),
                              int(c2 - r) : int(c2 + r + sup)]
        
    def ggrid_eval(self, params):
        """
        set gaussians on the predefined grids.
        Input:
        - params: array with the intensity and fwhm for each gaussian 
        """
        par = np.array(params).reshape(params.shape[0]/2, 2)
        c1, c2, i0 = self.par.getLocpar(self.id-1)
        cnt = 0
        self.psfg.reset()
        fault = False
        #inner grid:
        if self.inrad > 0:
            for i in xrange(int(c1 - self.inrad), int(c1 + self.inrad)+self.isuppix, self.idisp):
                for j in xrange(int(c2 - self.inrad), int(c2 + self.inrad)+self.isuppix, self.idisp):
                    if par[cnt,1] < self.fwhmin:
                        fault = True                    
                        break
                    self.psfg.addGaus_fnorm(par[cnt,1], i, j, i0*par[cnt,0], self.wr)
                    #here again, possibility to use a truncated gaussian
                    #self.psfg.addGaus_trunc(par[cnt,1], i, j, i0*par[cnt,0], self.wr)
                    cnt += 1  
        #outer grid:
        if self.outrad > 0:
            for i in xrange(int(c1 - self.outrad), int(c1 + self.outrad)+self.osuppix, self.odisp):
                for j in xrange(int(c2 - self.outrad), int(c2 + self.outrad)+self.osuppix, self.odisp):
                    if par[cnt,1] < self.fwhmin or fault == True:
                        fault = True
                        break                    
                    self.psfg.addGaus_fnorm(par[cnt,1], i, j, i0*par[cnt,0], self.wr)
                    #here again, possibility to use a truncated gaussian
                    #self.psfg.addGaus_trunc(par[cnt,1], i, j, i0*par[cnt,0], self.wr)
                    cnt += 1  
        if fault == True:
            #self.chig.fill(10000000000000.)
            self.chig = self.chig * 1000000000
        else:
            self.chig = (self.residuals - self._mean(self.psfg.array, self.bshape[0], self.bshape[1]))/self.image.noiseMap
    #############################################################################
    
    ########################### Centered gaussians algo #########################
    def setup_cgausfit(self, diameter, fwhmin):
        """
        prepare the parameters for the gaussian fit
        Inputs:
        - diameter: the diameter along which the gaussians will be placed 
        - fwhmin:   the minimal fwhm that the gaussians will be allowed to have
                    (not including the fwhm coming from the convolution)
        Output: returns an array of the size of the outer square containing
                the corresponding diffm values. (useful for the median computation)
        """
        self.gausrad = diameter/2
        self.fwhmin = fwhmin
        c1, c2, i0 = self.par.getLocpar(self.id-1)
        c1, c2 = int(c1/self.sampling_factor),int(c2/self.sampling_factor) 
        if c1 - diameter/2. < 0. or c2 - diameter/2. < 0. or c1 + diameter/2. >= self.bshape[0]  or c2 + diameter/2. >= self.bshape[1]:
            raise ValueError, 'Bad gaussian fit diameter'
        return self.diffm.array[int(c1 - self.gausrad) : int(c1 + self.gausrad),
                                int(c2 - self.gausrad) : int(c2 + self.gausrad)]
        
    def cgaus_eval(self, params):
        """
        set gaussians on the predefined grid.
        Input:
        - params: array with the intensity and fwhm for each gaussian 
        """
        par = np.array(params).reshape(params.shape[0]/2, 2)
        c1, c2, i0 = self.par.getLocpar(self.id-1)
        cnt = -1
        self.psfg.reset()
        fault = False
        for i in xrange(int(c1 - self.gausrad), int(c1 + self.gausrad)):
            for j in xrange(int(c2 - self.gausrad), int(c2 + self.gausrad)):
                cnt += 1  
                if par[cnt,1] < self.fwhmin:
                    fault = True             
                    break       
                self.psfg.addGaus_fnorm(par[cnt,1], i, j, i0*par[cnt,0], self.wr)
                #here again, possibility to use a truncated gaussian
                #self.psfg.addGaus_trunc(par[cnt,1], i, j, i0*par[cnt,0], self.wr)
        if fault == True:
            self.chig.fill(10**10)
        self.chig = (self.diffm.array - self._mean(self.psfg.array, self.bshape[0], self.bshape[1]))/self.image.noiseMap
    ############################################################################
    
    ############################## Numerical fit ################################
    def numeval(self, param):
        self.chinum = (self.diffnum.array) / self.image.noiseMap
        
    def num_step(self):
        self.diffnum.array -= self._mean(self.psfnum.array, self.bshape[0], self.bshape[1])
    ############################################################################
        
    
    def __set_diffnum(self):
        #not needed anymore
        self.diffnum.array = self.diffm.array.copy()
        
    def __build_diffnum(self, tab):
        #not needed anymore
        self.numeval(tab)
        self.diffnum.array = self.chinum
        
    #############  Private methods  ################
        
    def _rebin(self, a, newshape ):
        '''
        Rebin an array to a new shape.
        '''
        assert len(a.shape) == len(newshape)

        slices = [ slice(0,old, float(old)/new) for old,new in zip(a.shape,newshape) ]
        coordinates = np.mgrid[slices]
        indices = coordinates.astype('i')   #choose the biggest smaller integer index
        return a[tuple(indices)] / (float(newshape[0])/float(a.shape[0]))**2.


    def _mean(self, a, *args):
        '''
        rebin ndarray data into a smaller ndarray of the same rank whose dimensions
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
                 [')'] + ['.sum(%d)'%(i+1) for i in xrange(lenShape)] #+ \
#                 ['/factor[%d]'%i for i in xrange(lenShape)]
        return eval(''.join(evList))
        
        
    def _preset(self):
        """
        Finds the initial parameters of the moffat, via gaussian fit starting from a good guess...
        """ 
        import scipy.optimize
        
        c1 = int(self.image.array.shape[0]/2.)
        c2 = int(self.image.array.shape[1]/2.)
        w = 8.0
        
        cr = 2
        centraldata = self.image.array[c1-cr:c1+cr,c2-cr:c2+cr]
        i0 = np.median(centraldata)
        
        params =  0., w, 0.1, c1, c2, i0 # theta, fwhm, e, c1, c2, i0
        #print "PREFIT :", params
            
        errorfunction = lambda p: np.ravel((self._gaus(*p)(*np.indices(self.image.array.shape)) - self.image.array)/self.image.noiseMap)
        p, success = scipy.optimize.leastsq(errorfunction, params)
        
        #print "POSTFIT = ", p
            
        p[2] = abs(p[2]) + 0.01*(abs(p[2])<=0.01) # We don't want e to be to close to 0.0
         
        #par: [theta, fwhm, e, beta]
        par = np.array([p[0]%(2*np.pi), 
                     self.sampling_factor*p[1], 
                     p[2],
                     self.sampling_factor*(p[1] / (2. * np.sqrt(2.*np.log(2.))))])
        self.par.propose(*par)
        self.par.addLocpar(self.id, p[3]*self.sampling_factor, p[4]*self.sampling_factor, i0)



    def _preset2(self):
        """
        Another technique to find the initial parameters of the moffat, using
        first the 2nd moments and then fitting a gaussian on the star 
        """ 
        import scipy.optimize
        data = self.image.array * (self.image.array>0.)
        total = data.sum()
        X, Y = np.indices(data.shape)
        c1 = (X*data).sum()/total
        c2 = (Y*data).sum()/total
        col = data[:, int(c2)]
        width_x = np.sqrt(abs((np.arange(col.size)-c2)**2*col).sum()/col.sum())
        row = data[int(c1), :]
        width_y = np.sqrt(abs((np.arange(row.size)-c1)**2*row).sum()/row.sum())
        i0 = data.max()
        w = (width_x+width_y)/2.
        params =  0., w, 0.1, c1, c2, i0
        errorfunction = lambda p: np.ravel((self._gaus(*p)(*np.indices(data.shape)) - data)/self.image.noiseMap)
        p, success = scipy.optimize.leastsq(errorfunction, params)
        p[2] += 0.01*(p[2]==0.)
        #par: [theta, fwhm, e, beta]
        par = np.array([p[0]%(2*np.pi), 
                     self.sampling_factor*p[1], 
                     p[2],
                     self.sampling_factor*(p[1] / (2. * np.sqrt(2.*np.log(2.))))])
        self.par.propose(*par)
        self.par.addLocpar(self.id, p[3]*self.sampling_factor, p[4]*self.sampling_factor, i0)

    def _gaus(self, theta, fwhm, e, c1, c2, i0):
        """
        A basic gausssian function, not really optimized but called only once
        during the class initialization
        """
        #TODO: optimize
        _cos = np.cos(theta)
        _sin = np.sin(theta)
        xm = lambda x,y: (x-c1+0.5)*_cos - (y-c2+0.5)*_sin
        ym = lambda x,y: (x-c1+0.5)*_sin + (y-c2+0.5)*_cos
        sigx = np.sqrt((fwhm / (2. * np.sqrt(2.*np.log(2.))))**2 + (self.wr / (2. * np.sqrt(2.*np.log(2.))))**2)
        sigy = sigx /(1. - e**2)
        return lambda x,y: i0*np.exp(-(xm(x,y)/(np.sqrt(2.)*sigx))**2. - (ym(x,y)/(np.sqrt(2.)*sigy))**2.)
    
    
    
    
    
    
    
        
        
