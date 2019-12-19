import string, os, time
#from numpy import *
import numpy as np
import scipy.signal, sys
try:
    import pycuda.gpuarray as gpuarray
except:
    pass

try:
    import numdisplay
except:
    import stsci.numdisplay # for usage with anaconda
 
INF = float("infinity")

write = sys.stdout.write
flush = sys.stdout.flush
class Verbose(object):
    class __Singleton:
        def __init__(self, level):
            #0: no output outside errors and exceptions
            #1: minimum standard output
            #2: full information output
            #3: debug output
            #TODO: add other output streams
            self.level = level
        def __call__(self, verbosity, *msg):
            if verbosity <= self.level:
                s = []
                if len(msg)>0:
                    s += [3*(verbosity-1)*' ' + '|']
                    for m in msg:
                        e = m
                        if type(m) != type(''): e = repr(m)
                        s += [e + ' ']
                    if s[-1] == '-r ':
                        del s[-1]
                        s = ['\r']+s
                    else:
                        s += ['\n']
                else: s = ['\n']
                write(''.join(s))
                flush()
    instance = None
    
    def __new__(self):
        if not Verbose.instance:
            Verbose.instance = Verbose.__Singleton(3)
        return Verbose.instance

out = Verbose()    



def ask(msg, default, assertion, errmsg='', level=1):
    try:
        while 1:
            out(level, msg, '['+str(default)+']:', '-r')
            resp = raw_input()
            if string.strip(resp):
                if not(not resp.isdigit() and (resp.isalnum() or '.' in resp or '/' in resp  or '_' in resp or '\\'in resp)):
                    try:
                        assert assertion(eval(resp))
                    except:
                        out(1, errmsg, '-r') 
                    else:
                        return eval(resp)
                else:
                    return resp
            else:
                if type(default)==type(''):
                    return default
    #                return eval(default)
                return default
    except KeyboardInterrupt, EOFError:
        return 'quit'

def has_cuda():
    try:
        import pyfft, pycuda
    except ImportError:
        return False
    return True

def get_pyfft_plan(shape):
    try:
        from pyfft.cuda import Plan
    except ImportError:
        return None
    return Plan(shape, normalize=True, wait_for_finish=True)
   
def cuda_init(shape):
    try:
        import pyfft, pycuda
    except ImportError:
        out(2, 'No CUDA bindings found (pyfft). Using regular convolution modules')
        return None, None
    out(2, 'CUDA bindings found!')
    from pycuda.tools import make_default_context
#    import pycuda.gpuarray as gpuarray
    import pycuda.driver as cuda
    cuda.init() #@UndefinedVariable
    context = make_default_context()
    return context, get_pyfft_plan(shape)
   
def switch_psf_shape(psf, center='SW'):
    nx, ny = psf.shape
    ac1, ac2 = nx/2., ny/2.
    dx = dy = 0.
    if center == 'O':
        c1, c2 = nx/2.-0.5, ny/2.-0.5
        dx = dy = 0.5
    elif center == 'NE':
        c1, c2 = nx/2., ny/2.
    elif center == 'SW':
        c1, c2 = nx/2.-1., ny/2.-1.
        dx = dy = 1.
    
    s = np.zeros(psf.shape)
    dx, dy  = int(round(dx)) , int(round(dy))
    ac1, ac2  = int(round(ac1)) , int(round(ac2))
    c1, c2  = int(round(c1)) , int(round(c2))
    s[:ac1+dx, :ac2+dy] = psf[c1:, c2:]
    s[ac1+dx:, ac2+dy:] = psf[:c1, :c2]
    s[:ac1+dx, ac2+dy:] = psf[c1:, :c2]
    s[ac1+dx:, :ac2+dy] = psf[:c1, c2:]
    return s

def psf_gen(size, bak, mpar, gpar, gpos, gstrat, sfact=2.):
    import PSF
    nx, ny = size
    c1, c2 = nx/2., ny/2.
    psf = PSF.PSF((nx,ny), (c1,c2))
    out(3, 'Building the PSF...')
    psf.add_source(mpar, gpar, gpos, gstrat, (c1, c2, 1.))
    if size != bak.shape:
        out(3, 'Expanding the PSF...')
        psf.array[psf.c1-bak.shape[0]//2 : psf.c1+bak.shape[0]//2,
                  psf.c2-bak.shape[1]//2 : psf.c2+bak.shape[1]//2] += bak
    else:
        psf.array += bak
    out(3, 'Done. Creating splitted PSF (old style shape)...')
    s = switch_psf_shape(psf.array, 'SW')
    norm = psf.array.sum()
    psf.array /= norm
    return psf, s/norm

def conv(kernel, array):
    return scipy.signal.fftconvolve(kernel, array, mode='same')

def div(kernel, array):
    #TODO: implement a correct method
    return scipy.signal.deconvolve(array, kernel)

def conv_reg(kernel, array):
    if kernel.shape != array.shape:
        data = rebin(array, kernel.shape)
        res = scipy.signal.fftconvolve(kernel, data, mode='same')
        return mean(res, array.shape[0], array.shape[1])
    else:
        return scipy.signal.fftconvolve(kernel, array, mode='same')

def cuda_conv(plan, kernel, img):
    d1 = gpuarray.to_gpu(kernel.astype(np.complex64))
    d2 = gpuarray.to_gpu(img.astype(np.complex64))
    plan.execute(d1)
    plan.execute(d2)
    r = d1*d2
    plan.execute(r,inverse=True)
    return r.get().real

def cuda_fftdiv(plan, kernel, img):
    d1 = gpuarray.to_gpu(kernel.astype(np.complex64))
    d2 = gpuarray.to_gpu(img.astype(np.complex64))
    plan.execute(d1)
    plan.execute(d2)
    r = d2/d1
    plan.execute(r,inverse=True)
    return r.get().real

def cuda_conv_complex(plan, kernel, img):
    d1 = gpuarray.to_gpu(kernel)
    d2 = gpuarray.to_gpu(img)
    plan.execute(d1)
    plan.execute(d2)
    r = d1*d2
    plan.execute(r,inverse=True)
    return r.get().real
    
def getGpos(img, nmax, size, bounds=None, epos=None, cutoffs=None):
    im = img.copy()
    gpos = np.array([])
    c1, c2 = im.shape[0]/2., im.shape[1]/2.
    if bounds is not None:
        c1, c2, radius = bounds
        im[0:c1-radius,:].fill(0.)
        im[c1+radius:,c2-radius:c2+radius].fill(0.)
        im[c1-radius:,:c2-radius].fill(0.)
        im[c1-radius:,c2+radius:].fill(0.)
    if epos is not None:
        epos.shape = epos.shape[0]/2, 2   
        for p in epos:
            x, xx = int(p[0]+c1-size/2.), int(p[0]+c1+size/2.)
            y, yy = int(p[1]+c2-size/2.), int(p[1]+c2+size/2.)
            im[np.max(x, 0.) : np.min(xx, img.shape[0])+1,
               np.max(y, 0.) : np.min(yy, img.shape[1])+1].fill(0.)
    if cutoffs is not None:
        cut1, cut2 = cutoffs
    else:
        cut1 = im.min()
        cut2 = im.max()
    i = 0
    while i < nmax :
        min = im.min()
        max = im.max()
        val = max
        if abs(min)>max:
            val = min
        ind = np.where(im == val)
        posx, posy = ind[0][0], ind[1][0]
        if im[posx, posy] == 0.:
            out(2, 'Out of possibilities,', i, 'location(s) found')
            break
        if val <= cut2 and val >= cut1:
            gpos = np.append(gpos, (posx, posy))
            i += 1
        im[np.maximum(posx-size//2, 0) : np.minimum(posx+size//2, img.shape[0])+1,
           np.maximum(posy-size//2, 0) : np.minimum(posy+size//2, img.shape[1])+1].fill(0.)
    if i == nmax:
        out(2, i, 'out of', nmax, 'positions found')
    return gpos.reshape(gpos.shape[0]/2, 2), i

from PSF import PSF
def get_s_pos(data, psf, pos, sig=1., tol=1., gres=2., conv_fun=None):
    import scipy.optimize
    if conv_fun is None: conv_fun = conv
    i0 = data[pos[0],pos[1]]/20.
    mod = PSF(data.shape)
    def errfun(par):
        mod.reset()
        mod.addGaus_fnorm_trunc(gres, par[0], par[1], i0)
        return ((data - conv_fun(psf, mod.array))/sig).ravel()**2.
    res = scipy.optimize.leastsq(errfun, pos, maxfev = 300, warning=False)[0]
    return res


def rebin(a, newshape ):
    '''
    Rebin an array to a new shape.
    '''
    assert len(a.shape) == len(newshape)

    slices = [ slice(0,old, float(old)/new) for old,new in zip(a.shape,newshape) ]
    coordinates = np.mgrid[slices]
    indices = coordinates.astype('i')   #choose the biggest smaller integer index
    return a[tuple(indices)] / (float(newshape[0])/float(a.shape[0]))**2.

def mean(a, *args):
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
    
def gaussian(shape, fwhm, c1, c2, i0, fwhm0 = 0.):
        """
        Return a gaussian
        Inputs:
         - shape 
         - fwhm
         - c1
         - c2
         - i0
         - fwhm0: if this value is different from zero, the function will use it to simulate
                  a convolution. In practice it will add it to the basic FWHM of the gaussians
                  (default = 0.)
        """
        indexes = np.indices(shape)
        k = 2. * np.sqrt(2.*np.log(2.))
        sig_2 =  (fwhm  / k)**2.
        sig0_2 = (fwhm0 / k)**2.
        norm = sig_2/(sig_2+sig0_2)
        g = np.exp((-(indexes[0]-c1+0.5)**2. - 
                  (indexes[1]-c2+0.5)**2)/(2.*(sig_2+sig0_2)))
        return i0*g*norm
    
def gaus_ell(shape, fwhm0, theta, fwhm, e, c1, c2, i0):
    """
    A basic gausssian function, not really optimized but called only once
    during the class initialization
    """
    #TODO: optimize
    _cos = np.cos(theta)
    _sin = np.sin(theta)
    xm = lambda x,y: (x-c1+0.5)*_cos - (y-c2-0.5)*_sin
    ym = lambda x,y: (x-c1+0.5)*_sin + (y-c2-0.5)*_cos
    sigx = np.sqrt((fwhm / (2. * np.sqrt(2.*np.log(2.))))**2 + (fwhm0 / (2. * np.sqrt(2.*np.log(2.))))**2)
    sigy = sigx /(1. - e**2)
    g = lambda x,y: i0*np.exp(-(xm(x,y)/(np.sqrt(2.)*sigx))**2. - (ym(x,y)/(np.sqrt(2.)*sigy))**2.)
    return np.fromfunction(g, shape)
    
def sinc_filt(shape, fwhm, c1, c2, i0, fwhm0 = 0.):
    indexes = np.indices(shape)
    g = np.sinc(np.sqrt((indexes[0]-c1+0.5)**2. + 
                        (indexes[1]-c2+0.5)**2))
    return i0*g

def LG_filter(shape, fwhm, c1, c2):
        """
        Return the Laplacian of a gaussian
        Inputs:
         - shape 
         - fwhm
         - c1
         - c2
        """
        indexes = np.indices(shape)
        k = 2. * np.sqrt(2.*np.log(2.))
        sig_2 =  (fwhm  / k)**2.
        lapl = (-1./(np.pi*sig_2**2.))*((-(indexes[0]-c1+0.5)**2. - 
                                     (indexes[1]-c2+0.5)**2)/(2.*(sig_2)))
        g = np.exp((-(indexes[0]-c1+0.5)**2. - 
                  (indexes[1]-c2+0.5)**2)/(2.*(sig_2)))
        filt = lapl*g
        return filt / filt.sum()
    
def get_args(sysargs):
    l = len(sysargs)
    args = sysargs[:]
    options = ''
    del args[0]
    if l > 1:
        if args[0][0] == '-':
            options = args[0][1:]
            del args[0]
    if len(args) == 0:
        args = None
    return options, args
        
def checkDic(list, dict):
    for e in list:
        try:
            dict[e]
        except KeyError:
            dict[e]=None
def isNone(list, dict):
    checkDic(list, dict)
    bad = []
    for e in list:
        if dict[e] == None:
            bad += [e]
    return bad 
def isBad(needed, dict):
    res = {}
    checkDic(needed, dict)
    for e in dict:
        if e in needed and dict[e] == None:
            res[e] = 'bad'
        else:
            res[e] = 'ok'
    return res 
    
def check_namespace(vars, ns):
    err = []
    for v in vars:
        if v not in ns:# or ns[v] is None:
#            print "Error,", v,"is undefined in config file"
            err += [v]
    return err
    

def makepilimage(img, ztrans="log", cutoffs=(None,None)):
    import Image
    if cutoffs == (None,None):
        img.setzscale()#mode = 'auto')
        z1, z2 = img.z1,img.z2
    else:
        z1, z2 = cutoffs
    if ztrans not in ["log", "lin"]:
        raise RuntimeError, "makepilimage : ztrans must be log or lin"

    ztransarray = img.array.copy() # deep copy of the array
    ztransarray[ztransarray > z2] = z2
    ztransarray[ztransarray < z1] = z1
    maxpixelval = ztransarray.max()
    minpixelval = ztransarray.min()
    
    #    functions that map into [0, 255]
    def loggray(x, a, b):
        linval = 10.0 + 990.0 * (x-float(a))/(b-a)
        return (np.log10(linval)-1.0)*0.5 * 255.0
    def lingray(x, a, b):
        return (x-float(a))/(b-a) * 255.0

    ztransarray.ravel()
    if ztrans == "log" :
        ztransarray = np.array(map(lambda x: loggray(x, minpixelval, maxpixelval), ztransarray))
    if ztrans == "lin" :
        ztransarray = np.array(map(lambda x: lingray(x, minpixelval, maxpixelval), ztransarray))
    ztransarray.shape = img.array.shape
    gvarray = np.zeros(img.array.shape, dtype=np.uint8) # an array of 256 bit gray values
    ztransarray.round(out=gvarray)
    return Image.fromarray(gvarray.transpose()) # we make a PIL image out of this
    #    Now we are intentionally in the classical image processing convention.
    #    x = horizontal, y = vertical, but (0, 0) is upper left !
    #    But we will not notice this orientation change in pixel access until we export the image.

def array2fits(array, filename, header = None):
    import astropy.io.fits as pyfits
    if header is not None:
        hdu = pyfits.PrimaryHDU(array.transpose(), header)
        hdu.verify('fix')
    else:
        hdu = pyfits.PrimaryHDU(array.transpose())
    if os.path.isfile(filename):
        os.remove(filename)
    hdu.writeto(filename)
    
def array2ds9(array, frame=1, name=None, zscale=False):
    ds9frame = frame%16
    try:
        numdisplay.display(array.transpose(), z1=array.min(), z2=array.min(), 
                           name=name, frame=ds9frame, zscale=zscale, quiet=True)
    except IOError:
        import os, time
        os.system('ds9 &')
        while True:
            try:
                numdisplay.display(array.transpose(), z1=array.min(), z2=array.min(), 
                                   name=name, frame=ds9frame, zscale=zscale, quiet=True)
            except IOError:
                time.sleep(0.5)
            else:
                break
    
def array2png(array, filename, ztrans="log", cutoffs=(None,None)):
    #    You need to generate the pilimage first !
    import ImageOps, AImage
    pil = makepilimage(AImage.Image(array.copy()), ztrans, cutoffs)
    flippilimage = ImageOps.flip(pil)
    flippilimage.save(filename, "PNG")
    
def save_img(imgs, names, filename, min_size=(0,0)):
    import f2n
    sys.path.append('./src/lib')
    nb = len(imgs)
    assert nb == len(names)
    l = int(round(np.sqrt(nb)))
    c = int(nb/l + (nb%l != 0.))
    size_max = min_size
    for im in imgs:
        x, y = im.shape
        size_max = ((x>size_max[0])*x or size_max[0],
                    (y>size_max[1])*y or size_max[1])
    im_list = []
    for i in xrange(nb):
        im = f2n.f2nimage(imgs[i], verbose=False)
        im.numpyarray = rebin(im.numpyarray, size_max) #TODO: use upsample instead
        im.setzscale(z2='ex')
        im.makepilimage()
        im.writetitle(names[i])
        im_list += [im]
    im_list = [[im_list[i+c*j] for i in xrange(c) if i+c*j<nb] for j in xrange(l)]
    for i in xrange(nb, c*l):
        fim = f2n.f2nimage(np.zeros(size_max), verbose=False)
        fim.makepilimage()
        im_list[-1] += [fim]
    f2n.compose(im_list, filename)
    
def string2val(sdict):
    dict = sdict.copy()
    for entry in dict:
        val = dict[entry]
        if type(val) == type(''):
            isstring = False
            if val != 'None':
                if len(val) > 1 and val[0]=="'" and val[-1]=="'":
                    val = val[1:-1]
                if '/' in val or '_' in val or (val.isalnum() and not val.isdigit()): 
                    isstring = True
                elif '.' in val:
                    seq = val.split('.')
                    for s in seq:
                        if s != '' and s.isalnum() and not s.isdigit():        
                            isstring = True
            if isstring == False:
                exec('val='+val)
            dict[entry]=val
    return dict


def get_data(filename, directory=None, pos=None, transpose=True, sky = 0., retall = False): 
    import astropy.io.fits as pyfits
    import os
    if directory is None:
        cd = os.path.join(os.getcwd(),'results')
    else:
        cd = os.path.join(os.getcwd(), directory)
    path = os.path.join(cd, filename)
    hdulist = pyfits.open(path)
    #hdulist.verify('fix')
    if len(hdulist) != 1:
        raise RuntimeError, "extractfromfits : len(hdulist) > 1 not allowed"
    data = hdulist[0].data       # assumes the first extension is an image
    header = hdulist[0].header
    if transpose is True:
        data = data.transpose()            # get values from the subsection

    # WARNING ! The following line caused an issue with numpy 1.10. Fixed it using astype
    #data[:] += np.zeros(data.shape, dtype=np.float64)    # switch to 8 byte
    data = data.astype(np.float64)

    hdulist.close()
    if pos is not None:
        x,y,size = pos
        radius = int(size/2.)
        r = size-radius * 2.
        if x+radius+r >= data.shape[1] or y+radius+r >= data.shape[0] or x-radius<0 or y-radius<0:
            raise RuntimeError, 'extraction error: sides too close'
        if retall is True:
            return data[x-radius:x+radius+r, y-radius:y+radius+r] - sky, header
        return data[x-radius:x+radius+r, y-radius:y+radius+r] - sky
    if retall is True:
        return data - sky, header
    return data - sky

def get_ds9_mask(shape, show=False):
    import commands
    import string
    from matplotlib.nxutils import points_inside_poly #@UnresolvedImport
    
    mask = np.zeros(shape)
    ind = np.indices(shape)
    ind = zip(ind[0].ravel(),ind[1].ravel())
    out=string.split(commands.getoutput('xpaget ds9 regions'),'\n')
    for r in out:
        if r[0]!='#' and r[:6]!='global' and r[:3]!='XPA' and r[:8]!='physical':
            i = string.find(r,'(')
            type = r[:i]
            if type == 'polygon':
                vertices = eval(r[i+1:-1])
                vertices = [vertices[2*i:2*i+2] for i in range(len(vertices)/2)]
                mask += points_inside_poly(ind, vertices).reshape(shape)
            if type == 'circle':
                c1,c2,r = eval(r[i+1:-1])
                c = lambda x,y: (x-c1)**2. + (y-c2)**2. < r**2.
                mask += np.fromfunction(c, shape)
    if show: array2ds9(mask)
    return np.bool8(mask)
    
    
def getnoisemap(array, e_adu, std_deviation):
    """
    Building of the noise map (photon noise in each pixel) where
    e_adu is the gain of the CCD camera
    """
    """
    if any(self.array/e_adu + std_deviation**2 < 0.):
        raise ValueError, "Bad gain or standard deviation  parameter (probably too low, resp. too high)"
    self.noiseMap = sqrt(self.array/e_adu + std_deviation**2)
    """
    nm = np.sqrt(abs(array)/e_adu + std_deviation**2)
#    nm[array/nm<1.] = 1.
    return nm

def write_cfg(filename, var_dic):
    dic = var_dic.copy()
    f = open(filename, "r")
    out = ''
    while True:
        line = f.readline()
        if not line:
            break
        if len(line) > 2 and '=' in line:
            if line[-1] != '\n':
                line += '\n'
            name, val = line.split("=")
            name, val = string.strip(name), string.strip(val)
            if name in dic:
                if type(dic[name]) == type(''):
                    out += name + " = '" + str(dic[name]) + "'\n"
                else:
                    out += name + ' = ' + str(dic[name]) + '\n'
                del dic[name]
            else:
                out += line
        else:
            out += line
    if len(dic) > 0:
        for name in dic.keys():
            if type(dic[name]) == type(''):
                out += name + " = '" + str(dic[name]) + "'\n"
            else:
                out += name + ' = ' + str(dic[name]) + '\n'
    f.close()

    f = open(filename, "w" )
    f.write(out)
    f.close()

def get_moments(data):
    total = data.sum()
    X, Y = np.indices(data.shape)
    c1 = (X*data).sum()/total
    c2 = (Y*data).sum()/total
    col = data[:, int(c2)]
    width_x = np.sqrt(abs((np.arange(col.size)-c2)**2.*col).sum()/col.sum())
    row = data[int(c1), :]
    width_y = np.sqrt(abs((np.arange(row.size)-c1)**2.*row).sum()/row.sum())
    return c1+0.5, c2+0.5, width_x, width_y

def get_shifts(imgs, boxsize=10.):
    nimg = len(imgs)
    ref = imgs[0]
    shifts = [[0,0]]
    c11 = np.maximum(0, (ref.shape[0]-boxsize)//2)
    c12 = np.minimum(ref.shape[0], (ref.shape[0]+boxsize)//2)
    c21 = np.maximum(0, (ref.shape[1]-boxsize)//2)
    c22 = np.minimum(ref.shape[1], (ref.shape[1]+boxsize)//2)
    for i in xrange(nimg-1):
        im = np.flipud(np.fliplr(imgs[i+1]))
        corr = conv(ref, im)[c11:c12,c21:c22]
        c1, c2 = get_moments(corr)[:2]
        dx = c1+c11-ref.shape[0]/2 
        dy = c2+c21-ref.shape[1]/2
        shifts += [[dx,dy]]
#        array2ds9(corr, frame=i+1)
    return np.array(shifts)

def flatten(mlist):
    lst = mlist
    try:
        lst = mlist.tolist() #if mlist is a numpy array
    except: pass
    res = []
    for l in lst:
        if isinstance(l, list) or isinstance(l, tuple):
            res.extend(flatten(l))
        else:
            res.append(l)
    return res

def shift(image, offset_x, offset_y, interp_order = 3, mode='reflect'):
    """
    Shift the array to the given center (uses interpolation).
    Inputs:
     - c1, c2:         new center
     - interp_order:   interpolation order for the shifting
    """
    from scipy import ndimage
    w, h    = image.shape
    #get the offsets:
    indexes = np.indices(image.shape)
    xrange = indexes[0] + offset_x
    yrange = indexes[1] + offset_y
    #get the positions for each pixel in the new system:
    new_pos = np.array([np.ravel(xrange), np.ravel(yrange)])
    #shift:
    s = image.sum()
    t = ndimage.map_coordinates(image, new_pos, order=interp_order, mode=mode)
    #reshape:
    t.shape = w,h
    if s != 0:
        t *= s/t.sum()
    return t
    
def get_circ_mask(shape, radius, val_in, val_out):
    rc1, rc2 = shape[0]/2., shape[1]/2.
    c = lambda x,y: (x-rc1)**2. + (y-rc2)**2. < radius**2.
    mask = np.fromfunction(c, shape)
    return mask*val_in + (np.invert(mask))*val_out

def get_circ_mask_exp(shape, radius, exp=1.):
    if radius is None: radius = shape[0]*shape[1]
    rc1, rc2 = shape[0]/2., shape[1]/2.
    def l_fun(x,y):
        r = np.sqrt((x-rc1)**2. + (y-rc2)**2.)
        return (r<radius) + (r>=radius)/np.exp(r-radius)**exp
    return np.fromfunction(l_fun, shape)

def get_lambda(shape, radius, val):
    if radius is None: radius = shape[0]*shape[1]
    rc1, rc2 = shape[0]/2., shape[1]/2.
    def l_fun(x,y):
        r = np.sqrt((x-rc1)**2. + (y-rc2)**2.)
        return (r<radius)*val + (r>=radius)*val*(r-radius)
#        return (r<radius)*val + (r>=radius)*val*np.exp(r-radius)
    return np.fromfunction(l_fun, shape)
    
class Buffer():
    def __init__(self, maxlen=800):
        self.buf = ''
        self.maxlen = maxlen
        self.new = False
    def write(self, string):
        self.buf += string
        self.buf = self.buf[max(0,len(self.buf)-self.maxlen):]
        self.new = True
    def flush(self):
        pass
    def read(self):
        self.new = False
        return self.buf


