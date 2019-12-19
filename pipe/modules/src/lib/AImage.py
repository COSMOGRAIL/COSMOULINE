from scipy.stats import stats


__version__ = '0.3.5'
__date__ = '2009'
__author__ = "Tewes Malte - EPFL <malte.tewes@epfl.ch>   \
              Cantale Nicolas - EPFL <n.cantale@gmail.com>"




#import sys
import os
#import scipy as sp
import astropy.io.fits as pyfits
#from numpy import *
import numpy as np
import utils as fn


class Image:
    
    def __init__(self, numpyarray=None, shape = (0,0), noisemap=None, mask=None):
        """
        Class to play with images, in the form of 2D numpy arrays with import/export features.
        One principal objective is to take care about image orientations and crops etc, to get each pixel "right".
        
        
        The pixel indexing works as in iraf / ds9 : the image starts in the lower left corner with (0,0), first pixels ends with (1,1).
        
        Cutout regions work as with iraf's imcopy.
        
        """
        #TODO: change constructor into one taking optional parameters such as filename, etc.    
        self.z1 = 0.0
        self.z2 = 1000000.0     
        self.nm_z1 = 0.0
        self.nm_z2 = 1000000.0    
        self.pilimage = None
        self.noiseMap = None
        
        if np.any(numpyarray) == None:
            self.array = np.zeros(shape, dtype=np.float64)
        else:
            if not isinstance(numpyarray, np.ndarray):
                raise RuntimeError, "mtimage : please give me numpy arrays !"
            if numpyarray.ndim != 2:
                raise RuntimeError, "mtimage : your array is not 2D !"
            self.array = numpyarray.astype(np.float64)
            self.setzscale()
            if noisemap is not None:
                self.noiseMap = noisemap
                
        self.mask = mask.astype(bool) if mask is not None else np.zeros(self.array.shape, dtype=np.bool)
        
    
    def __str__(self):
        return_string = ["Shape : ", str(self.array.shape), "\nPixel type : ", str(self.array.dtype.name), "\nCutoffs : z1 = ", repr(self.z1), " z2 = ", repr(self.z2)]
        return ''.join(return_string)
    
      
    def showds9(self, ds9frame=1, noiseMap = False, imgname="image", ztrans="lin", zscale=False):
        #    Shows the array in ds9, with the original orientation.
        #    This bugs if the array is full of zeroes -> use showmatplot to display your zeros !
        fn.array2ds9(self.array, name=imgname, frame=ds9frame, zscale=zscale)
        
        
    def showmatplot(self):
        #import pylab
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        plt.matshow(self.array.transpose(), vmin=self.z1, vmax=self.z2, cmap=cm.hot, origin="lower", extent=(0, self.array.shape[0], 0, self.array.shape[1])) #@UndefinedVariable
        if self.noiseMap != None:
            plt.matshow(self.noiseMap.transpose(), vmin=self.nm_z1, vmax=self.nm_z2, cmap=cm.hot, origin="lower", extent=(0, self.array.shape[0], 0, self.array.shape[1])) #@UndefinedVariable
        # shape[1] and [0] are inverted due to the transpose ...
        plt.colorbar()
        plt.title(str(self.array.shape) + " " + str(self.array.dtype.name))
        plt.show()
        
    
    def showpilimage(self):
        import matplotlib.pyplot as plt
        if self.pilimage == None :
            import utils.makepilimage
            self.pilimage = utils.makepilimage(self.array, ztrans="log")
            print "No previous invocation of makepilimage: default ztrans = log"
        plt.imshow(self.pilimage, interpolation="nearest")
        plt.show()
    
    def writetopng(self, filename, ztrans="log", cutoffs=(None,None)):
        import utils
        utils.array2png(self.array, filename, ztrans, cutoffs)
    
    def writetofits(self, filename):
        hdu = pyfits.PrimaryHDU(self.array.transpose())
        if os.path.isfile(filename):
            os.remove(filename)
        hdu.writeto(filename)
        
    def writetofitsNM(self, filename):
        if self.noiseMap != None:
            hdu = pyfits.PrimaryHDU(self.noiseMap.transpose())
            if os.path.isfile(filename):
                os.remove(filename)
            hdu.writeto(filename)
        else: raise NameError, 'No noise map built' 

    def readfromfits(self, filename):
        """Puts the full fits file into the image"""
        self.array = pyfits.getdata(filename, 0).transpose() 
        #self.array = self.array + zeros(self.array.shape, dtype=float64)
        self.array = np.asarray(self.array, dtype=np.float64)
        #    This tansposition makes the pixelarray coordinates (x,y) equal to those in the ds9 display etc.
        #    In other words, we are in the math and astro convention.
        #    x = horizontal, y = vertical, (0, 0) is bottom left.
        self.setzscale()
        
        #print "Input max, min :", self.array.max(), self.array.min()

    def extractfromfits(self, filename, loc, size, sky=0.):
        """
        Extracts a subregion from a fits file  and converts it according
        to the astro and math convention: pixel (0,0) is at the bottom left
        """
        x, y = loc
        radius = int(size/2)
        r = size-radius * 2
        hdulist = pyfits.open(filename)  # open a FITS file
        if len(hdulist) != 1:
            raise RuntimeError, "extractfromfits : len(hdulist) > 1 not allowed"
        fulldata = hdulist[0].data       # assumes the first extension is an image
        if x< 0 or y< 0 or x>= fulldata.shape[1] or y>= fulldata.shape[0]:
            raise RuntimeError, "extractfromfits : bad extraction parameters"
        if x+radius+r >= fulldata.shape[1] or y+radius+r >= fulldata.shape[0] or x-radius<0 or y-radius<0:
            #TODO: set outside pixels to NaN
            print "outside"
        self.array = self.array + np.zeros(self.array.shape, dtype=np.float64)    # switch to 8 byte   
        self.array = fulldata[y-radius:y+radius+r, x-radius:x+radius+r].transpose()            # get values from the subsection 
        #    This tansposition makes the pixelarray coordinates (x,y) equal to those in the ds9 display etc.
        #    In other words, we are in the math and astro convention.
        #    x = horizontal, y = vertical, (0, 0) is bottom left.
        self.array[np.where(np.isnan(self.array))] = sky
        hdulist.close()
        if sky is None:
            #TODO: check...
            self.array -= stats.mode(self.array.ravel())[0][0]
        else:
            self.array -= sky
        self.setzscale()
        
    def normalize(self):
        """
        normalization of the image by its maximal value 
        """
        max = self.array.max()
        self.array = self.array / max
        self.setzscale()
        if self.noiseMap != None:
            #normalize noise maps
            self.noiseMap = self.noiseMap / max
            #neutralize the bad pixels
            for index, pix in np.ndenumerate(self.noiseMap):
                if pix == 0: self.noiseMap[index] = max*1000000
            self.nm_z1 = self.noiseMap.min()
            self.nm_z2 = self.noiseMap.max()
    
    def buildNoiseMap(self, e_adu, std_deviation):
        """
        Building of the noise map (photon noise in each pixel) where
        e_adu is the gain of the CCD camera
        """
        #TODO: put this into the constructor or create a subclass
        """
        if any(self.array/e_adu + std_deviation**2 < 0.):
            raise ValueError, "Bad gain or standard deviation  parameter (probably too low, resp. too high)"
        self.noiseMap = sqrt(self.array/e_adu + std_deviation**2)
        """
        #easy implementation, but doesn't detect cosmics
        self.noiseMap = np.sqrt(np.abs(self.array)/e_adu + std_deviation**2)
    
    def setzscale(self, mode = 'full', z1='0', z2='1'):
        if mode == 'full':
            self.z1 = self.array.min()
            self.z2 = self.array.max()
            if self.noiseMap != None:
                self.nm_z1 = self.noiseMap.min()
                self.nm_z2 = self.noiseMap.max()
        elif mode == 'man':
            self.z1 = z1
            self.z2 = z2
            if self.z2 < self.z1:
                raise ValueError, "setzscale: z2 < z1"
        elif mode == 'auto':
            #    This is a home built quick and dirty scaling optimal for typical PSF images.
            
            sky = np.median(self.array[[0, 1, -2, -1],:].flatten())
            sigsky = self.array[[0, 1, -2, -1],:].flatten().std()
            self.z1 = sky - 5*sigsky
        
            #self.z2 = 0.3 * self.array.max()
            self.z2 = 2.0 * self.array.mean()
            #self.z2
            
            if self.z2 < self.z1:
                raise ValueError, "autozscale: z2 < z1"
        else:
            raise ValueError, "Unknown Z scale mode"


    def getCenter(self, absolute=False, center_mode='SW', middle=False):
        """
        Compute the image Barycenter coordinates and set them into c1 and c2
        The formula used is:
            X = (Sum[p in image] Ip * xp) / Sum[p in image] Ip
            Y = (Sum[p in image] Ip * yp) / Sum[p in image] Ip 
        """
        if absolute == True:
            off = (not middle)/2.
            w, h    = self.array.shape
            if center_mode == 'NE':
                return w/2. + 0.5 - off, h/2. + 0.5 - off 
            elif center_mode == 'SW':
                return w/2. - 0.5 - off, h/2. - 0.5 - off 
            elif center_mode == 'O':
                return w/2., h/2.
            else: 
                raise ValueError, 'Unknown center mode, should be NE, SW or O'
        sumIx = 0
        sumIy = 0
        sumI = 0
        for index, val in np.ndenumerate(self.array):
            sumI  += val
            sumIx += val * index[0]
            sumIy += val * index[1]
        c1 = (sumIx / sumI)
        c2 = (sumIy / sumI)
        return c1,c2
                
    def shiftToCenter(self, c1, c2, interp_order = 3, center_mode = 'SW', ret = False, mode='wrap'):
        """
        Shift the array to the given center (uses interpolation).
        Inputs:
         - c1, c2:         new center
         - interp_order:   interpolation order for the shifting
         - center_mode:    where the new center should positioned. 
                           Possible values:
                               NE: on the center of the up and right pixel
                               NW: on the center of the down left pixel
                               O: on the classical origin (exact middle)
         - ret:            returns the new array if true, else set the image with it
        """
        from scipy import ndimage
        w, h    = self.array.shape
        c1      = float(c1)
        c2      = float(c2)
        #get the center:
        if center_mode == 'NE':
            x0   = w/2. + 0.5 
            y0   = h/2. + 0.5
        elif center_mode == 'SW':
            x0   = w/2. - 0.5 
            y0   = h/2. - 0.5
        elif center_mode == 'SW2':
            x0   = w/2. - 1.
            y0   = h/2. - 1.
        elif center_mode == 'O':
            x0   = w/2. 
            y0   = h/2.
        else: 
            raise ValueError, 'Unknown center mode, should be NE, SW or O'
        #get the offsets:
        offY = c2 - y0
        offX = c1 - x0
        indexes = np.indices(self.array.shape)
        xrange = indexes[0] + offX
        yrange = indexes[1] + offY
        #get the positions for each pixel in the new system:
        new_pos = np.array([np.ravel(xrange), np.ravel(yrange)])
        #shift:
        s = self.array.sum()
        t = ndimage.map_coordinates(self.array, new_pos, order=interp_order, mode=mode)
        #reshape:
        t.shape = w,h
        if s != 0:
            t *= s/t.sum()
        if ret is False:
            self.array = t
            try:
                s = self.noiseMap.sum()
                self.noiseMap = ndimage.map_coordinates(self.noiseMap, new_pos, order=1, mode=mode)
                self.noiseMap.shape = w,h
                self.noiseMap *= s/self.noiseMap.sum()
            except: 
#                print 'error in noise map interpolation'
                pass
        else:
            return t

# some ideas from imcat :
#'logscaleimag' reads a fits image f from stdin and calculates f0 * (b + a * log(1 + f / (a * sigma))) which is linear in f for small values (|f| < a few sigma) but compresses higher values. Useful for printing images.
