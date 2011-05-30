from numpy import *
import numpy.random as rd
import scipy.ndimage.interpolation, string, os

from lib.PSF import *
import lib.utils as fn
from lib.AImage import *


out = fn.Verbose()
#out.level = 3
def main():
    y = Y = Yes = yes = True
    n = N = No = no = False
    ask = fn.ask
    
    mofpos = []
    gauspos = []
    gaussians = []
    moffats = []
    psfpar = []
    
    out(1, 'Begining image creation!')
    size = ask('What is the final image size?', (128,128),
               lambda r: len(r)==2 and type(r[0]) == type(1) and type(r[1]) == type(1))
    
    
    galnb = ask('How many extended sources do you want?', 0,
                lambda r: r>=0)
    for i in xrange(galnb):
        out(2, 'Defining source', 1)
        pos = ask('Position?', (size[0]/2.,size[1]/2.),
                  lambda r: len(r)==2 and type(r[0]) == type(1) and type(r[1]) == type(1) and
                            r[0]<=size[0] and r[1]<=size[1],
                  level=3)
        mofpos += [array([pos[0],pos[1]])]
        moffats += [ask('Intensity, theta, width, ell, beta?', (1000., 2., 12., 0.5, 1.5),
                        lambda r: r[0]>0. and (type(r[1])==type(0) or type(r[1])==type(0.)) and 
                                  r[2]>0. and (type(r[3])==type(0) or type(r[3])==type(0.)) and
                                  r[4]>0. and len(r) < 6,
                        level=3)]
        out(3, (mofpos[i][0],mofpos[i][1]), 'added')
    
        
    srcnb = ask('How many point sources do you want?', 0,
                lambda r: r>=0)
    rnd = ask('Do you want them to be randomly distributed?', 'No',
              lambda r: r==0 or r == 1)
    if rnd:
        fwhm = ask('What is the sources\' resolution (same for all)?', 2.,
                   lambda r: type(r)==type(0) or type(r)==type(0.),
                   level=2)
        pad = ask('Force padding between the sources (padding)?', 'No',
                   lambda r: type(r)==type(0) or type(r)==type(0.),
                   level=2)
        
    if not rnd:
        fwhm = 0.
        for i in xrange(srcnb):
            out(2, 'Defining source', 1)
            pos = ask('Position?', (size[0]/2.,size[1]/2.),
                      lambda r: len(r)==2 and (type(r[0]) == type(1) or type(r[0]) == type(1.)) 
                                and (type(r[1]) == type(1) or type(r[0]) == type(1.)) and
                                r[0]<=size[0] and r[1]<=size[1],
                      level=3)
            gauspos += [array([pos[0],pos[1]])]
            gaussians += [ask('Intensity, FWHM?', (10000., 2.),
                              lambda r: r[0]>0. and r[1]>0.,
                              level=3)]
            out(3, (gauspos[i][0],gauspos[i][1]), 'added')
    
    
    conv = ask('Do you want the image to be convolved by a PSF?', 'No',
               lambda r: r==0 or r == 1)
    #           lambda r: type(r)==type(0) or type(r)==type(0.))
    if conv:
        psfpar = ask('The PSF used will be a simple Moffat. Would you like '
                     +'to change the default parameters? (theta, width, ell, beta)', (0., 4., 0., 2.),
                     lambda r:  (type(r[0])==type(0) or type(r[0])==type(0.)) and 
                                r[1]>0. and (type(r[2])==type(0) or type(r[2])==type(0.)) and
                                r[3]>0. and len(r) < 5,
                     level=2)
    
    #sky = ask('Do you want to use a sky (sky value)?', 'No',
    #          lambda r: type(r)==type(0) or type(r)==type(0.))
    sky = ask('Do you want to add a gaussian noise (sky value)?', 'No',
              lambda r: r>=0.)
    if not sky or sky=='No': sky=0.
    else: sky = eval(sky)
    sampling = ask('Do you want the resulting image to be under-sampled? ', 'No',
                   lambda r: r==0 or r == 1)
    if sampling:
        sampling = ask('By which factor? ', 2,
                       lambda r: r > 0.,
                       level=2)
        if sampling != 1.:
            out(2, 'Warning: all above parameters will be applied to SMALL pixels!')
    
    nbimg = ask('Multiple images (nb)?', 'No',
                lambda r: type(r)==type(0) or type(r)==type(0.))
    if not nbimg or nbimg=='No': nbimg=1
    
    
    out(1, 'Creating image...')
    out(2, 'Initializing arrays...')
    if type(size)==type(()):
        size = [size[0], size[1]]
    shape = size[:]
    if sampling:
        shape[0] *= sampling
        shape[1] *= sampling
        for p in gauspos:
            p[0]*=sampling
            p[1]*=sampling
        for p in mofpos:
            p[0]*=sampling
            p[1]*=sampling
    uni = PSF(shape)
    data = uni.array.copy()
    psf = PSF(shape)
    if conv:
        psf.set_finalPSF(fn.flatten([psfpar]), [], [], 'weighted', center='NE')
    
    
    imgs = []
    imsigs = []
    offsets = []
    #i_range = linspace(65050., 150.*(srcnb>=10)+20000.*(srcnb<10), srcnb)
    i_range = linspace(200000., 2000., srcnb)
    for j in xrange(nbimg):
        uni.reset()
        dx = rd.random()/2. * (j>0)
        dy = rd.random()/2. * (j>0)
        offsets += [dx,dy]
        out(2, 'Adding Moffats...')
        for i in xrange(galnb):
            uni.addMof(fn.flatten([moffats[i][1:]] + [mofpos[i][0]+dx,mofpos[i][1]+dy] + [moffats[i][0]]))
        out(2, 'Adding gaussians...')
        for i in xrange(srcnb):
            if rnd:
                if j == 0:
                    c1, c2 = random.rand(1)*shape[0], random.rand(1)*shape[1]
                    if pad:
                        padded = False
                        while not padded:
                            c1, c2 = random.rand(1)*shape[0], random.rand(1)*shape[1] #executing one time too many but I don't care...
                            padded =  c1 >= shape[0]*0.1 and c1 <= shape[0]*0.9
                            padded *= c2 >= shape[1]*0.1 and c2 <= shape[1]*0.9 
                            for p in gauspos:
                                padded *= sqrt((c1-p[0])**2. + (c2-p[1])**2.) >= pad
                    gauspos += [array([c1, c2])]
                    gaussians += [(i_range[i], fwhm)]
            uni.addGaus_basic(gaussians[i][1], gauspos[i][0]+dx, gauspos[i][1]+dy, gaussians[i][0])
            
        if conv:
            out(2, 'Convolving...')
    #        psf.array = fn.get_data('psf_h.fits','')
            data = fn.conv(psf.array, uni.array)
        else:
            data = uni.array.copy()
        imgs += [data]
    
    if sampling:
        out(2, 'Re-sampling to the desired resolution...')
        for i in xrange(nbimg):
            data = imgs[i]
            sum = data.sum()
            data = scipy.ndimage.interpolation.zoom(data, 1./sampling, order = 0, mode='reflect').astype('float64')
            data *= sum / data.sum()
            imgs[i] = data.copy()
        
    out(2, 'Creating sigma map...')
    for i in xrange(nbimg):
        sig = sqrt(abs(imgs[i]+sky))
        imsigs += [sig]
    
    if sky:
        out(2, 'Generating some noise...')
        for i in xrange(nbimg):
            imgs[i] += sqrt(abs(imgs[i]+sky))*rd.normal(0., 1., size)
        
    
    
    out(1, 'Done!!')
    
    
    show = ask('Do you want to see the result?', 'Y',
               lambda r: r==0 or r == 1)
    if show:
        for i in xrange(nbimg):
            fn.array2ds9(imgs[i], name='artificial_data', frame=i+1)
    
    save = ask('Do you want to save the result?', 'Y',
               lambda r: r==0 or r == 1)
    
    if save:
        import cPickle
        out(2, 'Output name [g.fits]:', '-r')
        name = raw_input()
        name = string.strip(name)
        if not name: name = 'g_'
        elif name[-6:] == '.fits' : name = name[:-6]
        name = os.path.join(os.path.join(os.getcwd(),'images'), name)
        for i in xrange(nbimg):
            fn.array2fits(imgs[i], name+str(i+1)+'.fits')
            fn.array2fits(imsigs[i], 'gsig_'+str(i+1)+'.fits')
        fname = os.path.join(os.path.join(os.getcwd(),'results'), 'true_par.dat')
        output = open(fname, 'wb')
        obj = {'mofpos':mofpos,
               'gauspos':gauspos,
               'gaussians':gaussians,
               'moffats':moffats,
               'psfpar':psfpar,
               'offsets':offsets}
        cPickle.dump(obj, output)
        output.close()
        out(2, 'Saved in', os.path.join(os.getcwd(),'results'))
    save = ask('Do you want to save the PSF?', 'Y',
               lambda r: r==0 or r == 1)
    if save:
        out(2, 'Output name [psf_1.fits]:', '-r')
        name = raw_input()
        name = string.strip(name)
        if not name: name = 'psf_1.fits'
        name = os.path.join(os.path.join(os.getcwd(),'results'), name)
        fn.array2fits(psf.array, name)
        fn.array2fits(fn.switch_psf_shape(psf.array), 's_1.fits')
        out(2, 'Saved in', os.path.join(os.getcwd(),'results'))
    
    out(1, 'Finished!')
    
    
if __name__ == "__main__":
    sys.exit(main())

    
    
    

