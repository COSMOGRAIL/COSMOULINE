
import numpy as np
import scipy.optimize

class Candidate():
    
    def __init__(self, x, y):
        self.id = 0
        self.x = x
        self.y = y
        self.rad = (0., 0., 0., 0.)
        self.img = None
        self.fwhm = 0.
        self.e = 0.
        self.rot = 0.
        self.chi = 0.
        self.grade = 1
        self.sig = None
    
    def __str__(self):
        s = ""
        s += "pos: (" + str(self.x) + ", " + str(self.y) + ") "
        s += "fwhm: "+ str(self.fwhm)
        s += " ellipticity: " + str(self.e)
        s += " rotation: " + str(self.rot)
        s += " chi2: " + str((self.chi**2.).sum())
        s += " grade: " + str(self.grade)
        return s
        
    def get_rad(self, data, mask):
        #TODO: check diags
        x, y = self.x, self.y
        rx_0 = 0
        rx_1 = 0
        ry_0 = 0
        ry_1 = 0
        v = data[x, y]
        oldv = v
        #TODO: set a threshold instead of comparing with the old value
        while(v <= oldv and x+rx_0 < data.shape[0] and mask[x+rx_0,y] != 0):
            oldv = v
            v = data[x + rx_0, y]
            rx_0 += 1
        v=data[x,y]
        oldv = v
        while(v <= oldv and x-rx_1 >= 0 and mask[x-rx_1,y] != 0):
            oldv = v
            v = data[x - rx_1, y]
            rx_1 += 1
        v=data[x,y]
        oldv = v
        while(v <= oldv and y+ry_0 < data.shape[1] and mask[x,y+ry_0] != 0):
            oldv = v
            v = data[x, y + ry_0]
            ry_0 += 1
        v=data[x,y]
        oldv = v
        while(v <= oldv and y-ry_1 >= 0 and mask[x,y-ry_1] != 0):
            oldv = v
            v = data[x, y - ry_1]
            ry_1 += 1
        self.rad = (rx_1, rx_0, ry_1, ry_0)
        return (rx_1, rx_0, ry_1, ry_0)
    
    def set_param(self, data, mask, sig=None, gain=None, sky = 0, usemom=False):
        x0, x1, y0, y1 = self.get_rad(data, mask)
        if (x0+x1)*(y0+y1) < 5:
            x1 += 1
            y1 += 1
        img = data[self.x-x0:self.x+x1, self.y-y0:self.y+y1].copy() #* mask[self.x-x0:self.x+x1, self.y-y0:self.y+y1]
        mask[self.x-x0:self.x+x1, self.y-y0:self.y+y1] = 0
        data[self.x-x0:self.x+x1, self.y-y0:self.y+y1] = sky
        self.img = img
        if abs(img).sum() == 0. :
            return 1
        if sig is not None and gain is not None:
            self.sig = np.sqrt(abs(img)/gain + sig**2)
        if not usemom:
            p = self.__get_fit(img)
        else:
            p = self.__get_mom(img)
        p[0] = p[0]%pi
        p[1] = abs(p[1])
        p[2] = abs(p[2])
        #p = [rot, fwhm, e]
        self.rot, self.fwhm, self.e = p[0:3]

    def get_par(self):
        return [self.fwhm, self.rot, self.e]

    def __get_mom(self, img):
        #TODO: change abs to + abs(min)
        total = np.abs(img).sum()
        X, Y = np.indices(img.shape)
        
#        c1 = (X*abs(img)).sum()/total
#        c2 = (Y*abs(img)).sum()/total
#        col = img[:, int(c2)]
#        width_x = sqrt(abs((arange(col.size)-c2)**2*col).sum()/col.sum())
#        row = img[int(c1), :]
#        width_y = sqrt(abs((arange(row.size)-c1)**2*row).sum()/row.sum())
#        width_xy = sqrt(abs((arange(col.size)-c2)*(arange(row.size)-c1)*row).sum()/row.sum())
#        r = 2.*sqrt(log(2.)*(width_x+width_y))
#        e = sqrt((width_x-width_y)**2.+(2.*width_y)**2.)


        mxx = (X**2*np.abs(img)).sum()/total
        myy = (Y**2*np.abs(img)).sum()/total
        mxy = (X*Y*np.abs(img)).sum()/total
        r = 2.*np.sqrt(np.log(2.)*(mxx+myy))
        e = np.sqrt((mxx-myy)**2.+(2.*myy)**2.)
        rot = 0.5*np.arctan(2.*mxy/(mxx-myy))
        self.chi = img
        return [rot, r, e]
        
    def __get_fit(self, img):
        total = np.abs(img).sum()
        X, Y = np.indices(img.shape)
        c1 = (X*np.abs(img)).sum()/total
        c2 = (Y*np.abs(img)).sum()/total
        col = img[:, int(c2)]
        width_x = np.sqrt(np.abs((np.arange(col.size)-c2)**2*col).sum()/col.sum())
        row = img[int(c1), :]
        width_y = np.sqrt(np.abs((np.arange(row.size)-c1)**2*row).sum()/row.sum())
        i0 = img.max()
        params =  0., (width_x+width_y)/2., 0.1, c1, c2, i0
        errorfunction = lambda p: np.ravel(self.__gaus(*p)(*np.indices(img.shape)) - img)
        if self.sig is not None:
            errorfunction = lambda p: np.ravel((self.__gaus(*p)(*np.indices(img.shape)) - img)/self.sig)
        p, success = scipy.optimize.leastsq(errorfunction, params, maxfev=100, warning=False)
        self.chi = (errorfunction(p)).reshape(img.shape)
        return p

    def __gaus(self, theta, fwhm, e, c1, c2, i0):
        _cos = np.cos(theta)
        _sin = np.sin(theta)
        sigx = (np.abs(fwhm) / (2. * np.sqrt(2.*np.log(2.))))
        sigy = sigx /(1. - e**2)
        return lambda x,y: i0*np.exp(-(((x-c1)*_cos - (y-c2)*_sin)/(np.sqrt(2.)*sigx))**2. - 
                                      (((x-c1)*_sin + (y-c2)*_cos)/(np.sqrt(2.)*sigy))**2.)
