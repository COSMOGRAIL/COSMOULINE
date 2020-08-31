

__version__ = '0.3.5'
__date__ = '2009'
__author__ = "Cantale Nicolas - EPFL <n.cantale@gmail.com>"

import numpy
from numpy import *
import weave

class PSF:
    def __init__(self, shape, center=None):
        """
        The PSF class contains a simple array and some methods to populate it
        with gaussians or moffat profiles
        Inputs:
         - shape: the shape of the array
         - center: the center of the gaussians
        """
        if center is None:
            center = (shape[0]/2.+0.5, shape[1]/2.+0.5)
        self.c1 = center[0]
        self.c2 = center[1]
        self.k = 2. * sqrt(2.*log(2.))
        self.peak1 = 0.
        self.peak2 = 0.
        self.peak3 = 0. 
        self.var1 = 0.
        self.var2 = 0.
        self.var3 = 4.*log(2.)
        self.var4 = 0.
        self.var5 = 0.
        self._sin = 0.
        self._cos = 0.
        shape = (int(round(shape[0])),int(round(shape[1])))
        self.array = zeros(shape).astype('float64')
        self.indexes = indices(shape)
        self.indexes2 = indices((32,32))
        self.ind = []
        for i in xrange(int(shape[0]*shape[1])):
            self.ind += [(i//shape[0],i%shape[1])]
        #polynoms (6th degree) used for the gaussian parameters (fwhm1, fwhm2, fwhm3, peak1, peak2, peak3)
        self.poly = array([[ -3.37565861e-05,   9.10960743e-04,  -1.01011591e-02,   5.90495767e-02, -1.93764661e-01,   3.57152802e-01,   4.45229001e-01],
                           [ -4.85456500e-05,   1.20713692e-03,  -1.17294586e-02,   5.36590605e-02, -9.41671007e-02,  -1.04025562e-01,   1.59619732e+00],
                           [  9.44428078e-05,  -3.18115588e-03,   4.53338257e-02,  -3.53362768e-01,  1.61889532e+00,  -4.31291275e+00,   7.14423236e+00],
                           [ -4.28585700e-05,   1.17724300e-03,  -1.32081237e-02,   7.68013474e-02, -2.37570756e-01,   3.23868646e-01,   3.14901896e-01],
                           [  1.36597486e-05,  -3.75735242e-04,   4.14754433e-03,  -2.27669152e-02,  5.82613647e-02,  -1.42974148e-02,   3.98038747e-01],
                           [  2.82613024e-05,  -7.74779549e-04,   8.74217796e-03,  -5.19903320e-02,  1.71759873e-01,  -2.94057056e-01,   2.72701311e-01]])
    
    def getCenter(self):
        """
        returns the origin of the array
        """
        return self.c1, self.c2
    
    def set_finalPSF(self, mofpar, gpar, gpos, gstrat, locpar = None, fwhm0=0.):
        self.reset()
        self.add_source(mofpar, gpar, gpos, gstrat, locpar, fwhm0)
        self.normalize()
    
    def add_source(self, mofpar, gpar, gpos, gstrat, locpar = None, fwhm0=0., flux=None):
        c1 = c2 = None
        i0 = 1.
        nx, ny = self.array.shape
        if locpar is not None:
            c1, c2, i0 = locpar
        else:
            c1, c2 = nx/2., ny/2.
        bak = None
        if flux is not None:
            bak = self.array.copy()
        self.addMof_fnorm(mofpar + [c1,c2,i0], fwhm0=fwhm0)
        if type(gpar)!= type(array([])) and type(gpos) != type(array([])):
            gpar, gpos = array(gpar), array(gpos)
        if gstrat not in ['grid', '2grids']:
            if fwhm0 != 0.:
                for i in xrange(gpar.shape[0]):
                    for j in xrange(gpar.shape[1]):
                        self.addGaus_fnorm_trunc(gpar[i,j,1], c1+gpos[i,j,0], c2+gpos[i,j,1], i0*gpar[i,j,0], fwhm0=fwhm0)
            else:
                for i in xrange(gpar.shape[0]):
                    for j in xrange(gpar.shape[1]):
                        self.addGaus_trunc(gpar[i,j,1], c1+gpos[i,j,0], c2+gpos[i,j,1], i0*gpar[i,j,0], fwhm0=fwhm0)
        if flux is not None:
            self.array = flux*self.array/self.array.sum() + bak
#        self.array *= i0 / self.array.sum()
        
    def setMof(self, param, fwhm0 = 0.):
        self.reset()
#        if fwhm0 != 0.:
#            self.addMof_fnorm(param, fwhm0)
#        else:
#            self.addMof(param)
        self.addMof_fnorm(param, fwhm0)
    
    def addMof_fnorm(self, param, fwhm0 = 0.):
        theta, width, ell, beta, c1, c2, i0 = param
        #go into the good reference:
        c1 -= 0.5
        c2 -= 0.5
        #update the instance parameters:
        self.c1 = c1
        self.c2 = c2
        #get the gaussian parameters from the moffat's beta parameter:
        fwhm1, fwhm2, fwhm3, self.peak1, self.peak2, self.peak3 = self._get_par(beta)
        #set the FWHMs and peaks to the scale:
        fwhm1 *= width
        fwhm2 *= width
        fwhm3 *= width
        self.peak1 *= (fwhm1**2.)/(fwhm1**2.+fwhm0**2.)
        self.peak2 *= (fwhm2**2.)/(fwhm2**2.+fwhm0**2.)
        self.peak3 *= (fwhm3**2.)/(fwhm3**2.+fwhm0**2.)
        self._sin = sin(theta)
        self._cos = cos(theta)
        self.var1 = c1*self._cos - c2*self._sin
        self.var2 = c1*self._sin + c2*self._cos
        var4 = (fwhm0/self.k)**2. 
        self.var5_1 = -2.*((fwhm1/self.k)**2. + var4)
        self.var5_2 = -2.*((fwhm2/self.k)**2. + var4)
        self.var5_3 = -2.*((fwhm3/self.k)**2. + var4)
        self.var6 = (ell**2. -1.)**2.
        self.array[:] += i0*fromfunction(self._gaus1, self.array.shape)
    
    def addMof(self, param, fwhm0 = 0.):
        """
        Computes an approximation of a moffat profile with 3 gaussians. The parameters
        of the gaussians emulate a [convolved] moffat.
        Inputs:
         - param: parameter of the moffat. Tuple or array containing in that order:
                      - theta:  rotation angle
                      - width:  FWHM of the moffat
                      - ell:    ellipticity
                      - beta:   power parameter of the moffat. The gaussians will try to
                                approximate this parameter
                      - c1, c2: center
                      - i0:     intesity
         - fwhm0: if this value is different from zero, the function will use it to simulate
                  a convolution. In practice it will add it to the basic FWHM of the gaussians
                  (default = 0.)
        """
        #get the parameters from the arguments:
        theta, width, ell, beta, c1, c2, i0 = param
        #go into the good reference:
        c1 -= 0.5
        c2 -= 0.5
        #update the instance parameters:
        self.c1 = c1
        self.c2 = c2
        #get the gaussian parameters from the moffat's beta parameter:
        fwhm1, fwhm2, fwhm3, self.peak1, self.peak2, self.peak3 = self._get_par(beta)
        #set the FWHMs and peaks to the scale:
        fwhm1 *= width
        fwhm2 *= width
        fwhm3 *= width
        self.peak1 *= i0
        self.peak2 *= i0
        self.peak3 *= i0
        #the next part is an attempt to optimization but it may still be improved with a better
        #understanding of python's overheads management
        #pre-comuptes constant values: 
        self._sin = sin(theta)
        self._cos = cos(theta)
        self.var1 = c1*self._cos - c2*self._sin
        self.var2 = c1*self._sin + c2*self._cos
        var4 = (fwhm0/self.k)**2. 
        self.var5_1 = -2.*((fwhm1/self.k)**2. + var4)
        self.var5_2 = -2.*((fwhm2/self.k)**2. + var4)
        self.var5_3 = -2.*((fwhm3/self.k)**2. + var4)
        self.var6 = (ell**2. -1.)**2.
        #computes the gaussians:
        self.array[:] += fromfunction(self._gaus1, self.array.shape)
        
    def setGaus_basic(self, fwhm, c1, c2, i0, fwhm0 = 0.):
        """
        set the array with a [convolved] gaussian
        Inputs: 
         - fwhm
         - c1
         - c2
         - i0
         - fwhm0: if this value is different from zero, the function will use it to simulate
                  a convolution. In practice it will add it to the basic FWHM of the gaussians
                  (default = 0.)
        """
        sig = (fwhm / (2. * sqrt(2.*log(2.))))**2. + (fwhm0 / (2. * sqrt(2.*log(2.))))**2.
        g = lambda x,y: i0*exp((-(x-c1+0.5)**2. - (y-c2+0.5)**2)/(2.*sig))
        self.array[:] = fromfunction(g, self.array.shape) 
    
    def addGaus_basic(self, fwhm, c1, c2, i0, fwhm0 = 0.):
        """
        add a [convolved] gaussian to the array 
        Inputs: 
         - fwhm
         - c1
         - c2
         - i0
         - fwhm0: if this value is different from zero, the function will use it to simulate
                  a convolution. In practice it will add it to the basic FWHM of the gaussians
                  (default = 0.)
        """
        #sigma:
        sig = (fwhm / (2. * sqrt(2.*log(2.))))**2. + (fwhm0 / (2. * sqrt(2.*log(2.))))**2.
        #gaussian:
        self.array[:] += i0*exp((-(self.indexes[0]-c1+0.5)**2. - (self.indexes[1]-c2+0.5)**2)/(2.*sig))
#        tmp = exp((-(self.indexes[0]-c1)**2. - (self.indexes[1]-c2)**2)/(2.*sig))
#        tmp[:] = tmp / abs(tmp).sum() 
#        self.array += i0*tmp
        
    def addGaus_fnorm(self, fwhm, c1, c2, i0, fwhm0 = 0.):
        """
        Add a [convolved] gaussian to the array, with flux conservation.
        See addGaus_basic()
        """
        sig_2 =  (fwhm  / self.k)**2.
        sig0_2 = (fwhm0 / self.k)**2.
        norm = sig_2/(sig_2+sig0_2)
        g = exp((-(self.indexes[0]-c1+0.5)**2. - 
                  (self.indexes[1]-c2+0.5)**2)/(2.*(sig_2+sig0_2)))
        self.array[:] += i0*g*norm
        
#        code = """
#        #include <math.h>
#        long double sig_2 = pow(((double)fwhm/(double)k),2.); 
#        long double sig0_2 = pow(((double)fwhm0/(double)k),2.);
#        long double norm = sig_2/(sig_2+sig0_2);
#        for(int x=0; x<(long double)nx; x++){
#            for(int y=0; y<(double)ny; y++){
#                data(x,y) += (double)i0*norm*exp((-pow((x-(double)c1),2.) - pow((y-(double)c2),2.))/(2.*(sig_2+sig0_2)));
#            }
#        }
#        """
#        data = self.array
#        k = self.k
#        nx, ny = self.array.shape
#        weave.inline(code,
#                     ['data','fwhm','fwhm0','nx','ny', 'i0', 'c1', 'c2', 'k'],
#                     verbose        =0,
#                     type_converters=weave.converters.blitz,
#                     compiler       ='gcc')
        
    def addGaus_fnorm_trunc(self, fwhm, c1, c2, i0, fwhm0 = 0.):
        """
        Add a [convolved] truncated gaussian to the array. The size of the computed gaussian
        corresponds to 3 times the cumulated FWHMs. Please note that no border check is made
        so please give correct FWHMs (not too high)
        Inputs: 
         - fwhm
         - c1
         - c2
         - i0
         - fwhm0: if this value is different from zero, the function will use it to simulate
                  a convolution. In practice it will add it to the basic FWHM of the gaussians
                  (default = 0.)
        """
        c1 -= 0.5
        c2 -= 0.5
        sig_2 =  (fwhm  / self.k)**2.
        sig0_2 = (fwhm0 / self.k)**2.
        norm = i0*sig_2/(sig_2+sig0_2)
        l = 5.*fwhm
        t11, t12, t21, t22 = int(c1-l), int(c1+l), int(c2-l), int(c2+l)
        self.array[t11:t12,t21:t22] += exp((-(self.indexes[0][t11:t12,t21:t22]-c1)**2. - 
                  (self.indexes[1][t11:t12,t21:t22]-c2)**2.)/(2.*(sig_2+sig0_2)))*norm
#        g = exp((-(self.indexes[0][t11:t12,t21:t22]-c1)**2. - 
#                  (self.indexes[1][t11:t12,t21:t22]-c2)**2.)/(2.*(sig_2+sig0_2)))
#        self.array[t11:t12,t21:t22] += i0*g*norm
    def addGaus_trunc(self, fwhm, c1, c2, i0, fwhm0 = 0.):
        """
        Add a [convolved] truncated gaussian to the array. The size of the computed gaussian
        corresponds to 3 times the cumulated FWHMs. Please note that no border check is made
        so please give correct FWHMs (not too high)
        Inputs: 
         - fwhm
         - c1
         - c2
         - i0
         - fwhm0: if this value is different from zero, the function will use it to simulate
                  a convolution. In practice it will add it to the basic FWHM of the gaussians
                  (default = 0.)
        """
        c1 -= 0.5
        c2 -= 0.5
        sig_2 =  (fwhm  / self.k)**2.
        sig0_2 = (fwhm0 / self.k)**2.
        norm = i0
        l = 5.*fwhm
        t11, t12, t21, t22 = int(c1-l), int(c1+l), int(c2-l), int(c2+l)
        self.array[t11:t12,t21:t22] += exp((-(self.indexes[0][t11:t12,t21:t22]-c1)**2. - 
                  (self.indexes[1][t11:t12,t21:t22]-c2)**2.)/(2.*(sig_2+sig0_2)))*norm
    
    def _gaus1(self, x,y):
        return self.peak1*exp(((self.var1 - x*self._cos + y*self._sin)**2. + 
                              ((self.var2 - x*self._sin - y*self._cos)**2.)*
                              self.var6)/self.var5_1) + self._gaus2(x,y)
        
    def _gaus2(self, x,y):
        return self.peak2*exp(((self.var1 - x*self._cos + y*self._sin)**2. + 
                              ((self.var2 - x*self._sin - y*self._cos)**2.)*
                              self.var6)/self.var5_2) + self._gaus3(x,y)
        
    def _gaus3(self, x,y):
        return self.peak3*exp(((self.var1 - x*self._cos + y*self._sin)**2. + 
                              ((self.var2 - x*self._sin - y*self._cos)**2.)*
                              self.var6)/self.var5_3)
        
        
    def _get_par(self, beta):
        """
        Comutes the gaussian parameters out of the moffat's beta parameter
        Input:
         - beta
        Output:
         - array containing the guassian parameters. In that order:
                - fwhm1, fwhm2, fwhm3, peak1, peak2, peak3
        """
        res = zeros(6)
        for i in xrange(6):
            res[i] = polyval(poly1d(self.poly[i]), beta)
        return res
        
    def normalize(self, i0=1.):
        self.array[:] *= i0 / self.array.sum() 
        
    def reset(self):
        """
        Fill the array with zeros
        """
        self.array.fill(0.)
        
        
    def getGaus_ell(self, fwhm0, theta, fwhm, e, i0):
        """
        Returns the function of an elliptical gaussian
        """
        _cos = cos(theta)
        _sin = sin(theta)
        xm = lambda x,y: (x-self.c1)*_cos - (y-self.c2)*_sin
        ym = lambda x,y: (x-self.c1)*_sin + (y-self.c2)*_cos
        sigx = sqrt((fwhm / (2. * sqrt(2.*log(2.))))**2. + (fwhm0 / (2. * sqrt(2.*log(2.))))**2.)
        sigy = sigx /(1. - e**2)
        return lambda x,y: i0*exp(-(xm(x,y)/(sqrt(2.)*sigx))**2. - (ym(x,y)/(sqrt(2.)*sigy))**2.)
        
        
        
        
        
        
        
