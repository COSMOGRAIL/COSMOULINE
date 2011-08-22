      

__version__ = '0.1.1'
__date__ = '2009'
__author__ = "Cantale Nicolas - EPFL <n.cantale@gmail.com>"
        
        
#from numpy import *
import numpy as np
        
class Param():
    """
    This class is a data structure containing the parameters of the 
    PSFs and useful methods to manage them.
    This class is intended to be used as a 'static' variable
    in the PSFs instances (i.e. they only keep a reference of one 
    instance and thus access the same data)
    """
    def __init__(self, mof_nb, gaus_nb, mof_length=4, gaus_length=3, loc_length=3):
        self.mofpar     = np.array([])
        self.gauspar    = np.array([])
        self.locpar     = np.array([])
        self.cons       = np.array([])
        self.opt_par    = np.array([])
        self.mofnb      = mof_nb
        self.moflen     = mof_length
        self.locnb      = 0
        self.loclen     = loc_length
        self.gausnb     = gaus_nb
        self.gauslen    = gaus_length
        self.consnb     = 0
    
    def toArray(self, i = -1):
        if i == -1:
            return np.append(self.mofpar, np.append(self.gauspar, self.locpar))
        elif i < self.mofnb:
            return np.append(self.mofpar[i], self.locpar)
        else:
            return np.append(self.gauspar[i-self.mofnb], self.locpar)
    
    def fromArray(self, tab, i = -1):
        """
        Get the moffat parameters out of the minimalization parameters. 
        Beware:
        -It is assumed that the entry is already ordered by the PSFs' id.
        -Because of the need for speed, no length verification will be made
         Please set the optional parameters during the creation if you use 
         directly the fromArray() method 
        """
        self.locnb = int((len(tab)-4)/self.loclen)
        if i == -1:
            k = self.mofnb*self.moflen
            j = k + self.gausnb*self.gauslen
            self.mofpar     = tab[:k].reshape(self.mofnb, self.moflen)
            self.gauspar    = tab[k:j].reshape(self.gausnb, self.gauslen)
            self.locpar     = tab[j:].reshape(self.locnb, self.loclen)
        elif i <= self.mofnb:
            self.mofpar[i-1]  = tab[:self.moflen]
            self.locpar       = tab[self.moflen:].reshape(self.locnb, self.loclen)
        else:
            self.gauspar[i-self.mofnb-1] = tab[:self.gauslen]
            self.locpar = tab[self.gauslen:].reshape(self.locnb, self.loclen)

    def addLocpar(self, pos, *param):
        self.loclen = len(param)
        if pos > self.locnb:
            self.locnb += 1
            self.locpar = np.append(self.locpar, np.array(param)).reshape(self.locnb, self.loclen)
        else:
            self.locpar[id-1] = np.array(param)
    
    def setLocpar(self, pos, *param):
        self.addLocpar(pos, *param)
        
    def getLocpar(self, i):
        return self.locpar[i]

    def addMofpar(self, *param):
        self.moflen = len(param)
        self.mofpar = np.append(self.mofpar, np.array(param)).reshape(self.mofnb, self.moflen)
    
    def setMofpar(self, i, *param):
        self.mofpar[i] = np.array(param)
        
    def getMofpar(self, i):
        return self.mofpar[i]
    
    def addGauspar(self, *param):
        self.gauslen = len(param)
        self.gauspar = np.append(self.gauspar, np.array(param)).reshape(self.gausnb, self.gauslen)

    def setGauspar(self, i, *param):
        self.gauspar[i] = np.array(param)
    
    def getGauspar(self, i):
        return self.gauspar[i]
        
    def setOptpar(self, *param):
        self.opt_par = np.array(param)
        self.fromArray(np.array(param))
        
    def propose(self, *param):
        """
        Note that there is no reset of the proposition but when setMofpar() is called.
        We don't keep track of who proposed what, it is assumed that each PSF proposes
        one set of parameters
        """
        self.consnb += 1
        tab = np.array(param)
        self.cons = np.append(self.cons, tab).reshape(self.consnb, len(param))
        tot = np.zeros(len(param), dtype = np.float64)
        for i in xrange(self.consnb):
            tot += self.cons[i]
        tot = tot / self.consnb
        k = self.mofnb*self.moflen
        j = k + self.gausnb*self.gauslen
        self.mofpar     = tot[:k].reshape(self.mofnb, self.moflen)
        self.gauspar    = tot[k:j].reshape(self.gausnb, self.gauslen)
        
    def getCenter(self, i):
        return self.locpar[i,0], self.locpar[i,1]





