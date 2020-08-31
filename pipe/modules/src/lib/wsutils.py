
import os
import utils as fn
import numpy as np
from numpy import *

out = fn.Verbose()
res_dir = 'results'

def clean_workspace(as_exe=False):
    cd = os.getcwd()
    if not as_exe: cd = os.path.join(cd, res_dir)
    ls = os.listdir(cd)
    for e in ls:
        if os.path.isfile(os.path.join(cd, e)) and (('.fits' in e) or ('.png' in e)):
            out(3, 'deleting '+e)
            if e != 'in.fits':#temp!!
                os.remove(os.path.join(cd, e))
        

def setup_workspace():
    try:
        os.mkdir('images')
        os.mkdir('results')
    except OSError:
        #already existing directorries
        pass
    


def backup_workspace(cfgfile, name=None, as_exe=False):
    import shutil
    cd = os.getcwd()
    if not as_exe: cd = os.path.join(cd, res_dir)
    ls = os.listdir(cd)
    files = [e for e in ls
             if os.path.isfile(os.path.join(cd, e))]
    if len(files) > 0:
        i = 1
        if name is None:
            while i < 1000:
                n = '0'*(1-i//100) + '0'*(1-i//10) + str(i)
                try:
                    os.mkdir(os.path.join(cd,n))
                    out(3, 'Directory '+n+'/ created')
                    break
                except OSError:
                    i += 1
        else: 
            cd = os.path.join(cd, name)
        out(3, 'Copying .fits files...')
        for f in files:
            if ('.fits' in f) or ('.png' in f):
                shutil.copy(os.path.join(cd,f), 
                            os.path.join(os.path.join(cd, n), f))
        out(3, 'Copying configuration file...')
        shutil.copy(os.path.join(os.getcwd(),cfgfile), 
                    os.path.join(os.path.join(cd, n), cfgfile))
    
def get_files(filename, directory=None, excl=None, as_exe=False):
    import string
    cd = directory
    if cd is None:
        cd = os.path.join(os.getcwd(),'results')
    if as_exe:
        cd = os.getcwd()
        res_dir = './'
    files = []
    cat = []
    if '*' not in filename:
        if not os.path.isfile(os.path.join(cd, filename)):
            raise IOError, 'No such file: '+filename
        files += [filename]
        cat += ['']
    else:
        s = string.split(filename, '*')
        if len(s) > 2: raise ValueError, 'filename error: only one "*" accepted' 
        lf = [e for e in os.listdir(cd)
              if os.path.isfile(os.path.join(cd, e))]
        for f in lf:
            if s[0] == f[0:len(s[0])] and (len(s[1])==0 or s[1] == f[-len(s[1]):]):
                c = f[len(s[0]) : len(f)-len(s[1])]
#                if excl is None:# or (excl is not None and excl not in c):
                stop = False
                if type(excl)==type(''):
                    stop = stop or excl in c
                if type(excl)==type([]):
                    for e in excl:
                        stop = stop or e in c
                if not stop: 
                    files += [f]
                    cat += [c]
    return sorted(files), sorted(cat)

def populate(filename, spos, npix, opos, orad, sky, sig, gain, clean=0, as_exe=False):
    #TODO: add debug info
    def extract(data, pos, size):
        x,y = pos
        radius = size//2
        r = size-radius * 2.
        if x+radius+r > data.shape[0] or y+radius+r > data.shape[1] or x-radius<0 or y-radius<0:
            raise RuntimeError, 'extraction error: sides too close'
        return data[x-radius:x+radius+int(round(r)), y-radius:y+radius+int(round(r))]
    if as_exe:
        cd = './'
        cdim = './'
        res_dir = './'
    else:
        cd = os.path.join(os.getcwd(),'results')
        cdim = os.path.join(os.getcwd(),'images')
    if '*' in filename:
        files, cat = get_files(filename, cdim)
    else:
        files, cat = [filename], ['']
    out(3, 'Found', repr(len(cat)), 'files')
    lname = lambda n, i, j: n+cat[i] +'_'+ '0'*(1-j//100) + '0'*(1-j//10) + str(j+1) + '.fits'
    if sky is None: sky = 0.
    try: sky[0]
    except TypeError: sky = [sky for f in files]
    if sig is None: sig = 0.
    try: sig[0]
    except TypeError: gain = [sky for f in files]
    try: gain[0]
    except TypeError: gain = [gain for f in files]
    
    for i, f in enumerate(files):
        out(2, 'Opening '+f)
        data = fn.get_data(f, directory=cdim, sky=sky[i])
        out(2, 'Extracting objects...')
        for j, s in enumerate(spos):
            out(3, 'Extracting star', s)
            try:
                d = extract(data, s, npix)
            except RuntimeError:
                out(2, 'Extraction error for the star', j+1, ': sides too close. Position:', s, 'Size:', npix)
            else:
                name = lname('star', i, j)
                if clean == 1:
                    d[where(isnan(d))] = sky[i]
                else:
                    if any(isnan(d)):
                        out(2, 'Warning: the star', j+1,' in *'+cat[i]+'* file contains NaN values')
                fn.array2fits(d, os.path.join(cd,name))
                fn.array2fits(np.zeros(d.shape, dtype=int), 
                              os.path.join(cd,lname('starmask', i, j)))
                if sig is not None and gain is not None:
                    s = fn.getnoisemap(d, gain[i], sig[i])
                    name = lname('starsig', i, j)
                    fn.array2fits(s, os.path.join(cd,name))
        #TODO: add compatibility mode for the naming
        #name = 'g'+'0'*(1-i//100) + '0'*(1-i//10) + str(i+1)+ '.fits'
        out(3, 'Extracting object')
        name = 'g_' + cat[i] + str(i+1) + '.fits'
        d = extract(data, opos, orad)
        if clean == 1:
            d[where(isnan(d))] = sky[i]
        else:
            if any(isnan(d)):
                out(2, 'Warning: the data contains NaN values')
        fn.array2fits(d, os.path.join(cd,name))
        fn.array2fits(np.zeros(d.shape, dtype=int), 
                      os.path.join(cd,'gmask_'+cat[i] + str(i+1) + '.fits'))
        if sig is not None and gain is not None:
            s = fn.getnoisemap(d, gain[i], sig[i])
            #name = 'sig'+'0'*(1-i//100) + '0'*(1-i//10) + str(i+1)+ '.fits'
            name = 'gsig_'+cat[i] + str(i+1) + '.fits'
            fn.array2fits(s, os.path.join(cd,name))
    return len(cat)
        

def getfilenames(nbsets=1, as_exe=False):
    stars, cat = get_files('star*.fits', excl = ['sig', 'mask'], as_exe=as_exe)
    stars= sorted(set(stars))
    sigs = sorted(set(get_files('starsig*.fits', as_exe=as_exe)[0]))
    masks = sorted(set(get_files('starmask*.fits', as_exe=as_exe)[0]))
    objs = sorted(set(get_files('g_*.fits', excl='sig', as_exe=as_exe)[0]))
    objsigs = sorted(set(get_files('gsig*.fits', as_exe=as_exe)[0]))
    objmasks = sorted(set(get_files('gmask*.fits', as_exe=as_exe)[0]))
    psfs = sorted(set(get_files('psf_*.fits', excl =['num','ini'], as_exe=as_exe)[0]))
    if as_exe:
        res_dir = './'
    if nbsets >1:
        snb = len(stars)//nbsets
        onb = len(objs)//nbsets
        stars = [stars[i*snb : (i+1)*snb] 
                 for i in range(nbsets)]
        sigs = [sigs[i*snb : (i+1)*snb] 
                for i in range(nbsets)]
        masks = [masks[i*snb : (i+1)*snb] 
                for i in range(nbsets)]
        objs = [objs[i*onb : i*onb+1] 
                for i in range(nbsets)]
        objsigs = [objsigs[i*onb : i*onb+1] 
                  for i in range(nbsets)]
        objmasks = [objmasks[i*onb : i*onb+1] 
                  for i in range(nbsets)]
        psfs = [psfs[i*onb : i*onb+1] 
                  for i in range(nbsets)]
    return stars, sigs, masks, objs, objsigs, objmasks, psfs

def get_filenb(filename):
    if type(filename) == type([]):
        return len(filename)
    return len(get_files(filename, directory='images')[1])


def restore(stars=None, sigs=None, masks=None, objs=None, objssig=None, objsmasks=None, psfs=None, as_exe=False):
    data = {'stars':None, 'sigs':None, 'masks':None, 'objs':None, 'objssigs':None, 'objsmasks':None, 'psfs':None}
    if as_exe:
        cd = './'
        res_dir = './'
    else:
        cd = os.path.join(os.getcwd(),'results')
    def fill(files, name):
        if files is not None and files != []:
            upli = []
            if type(files[0]) == type([]):
                for sf in files:
                    li = []
                    for s in sf:
                        li += [fn.get_data(os.path.join(cd, s),'./')]
                    upli += [li]
                data[name] = upli
            else:
                for s in files:
                    upli += [fn.get_data(os.path.join(cd, s),'./')]
                data[name] = [upli]
    fill(stars,'stars')
    fill(sigs, 'sigs')
    fill(masks, 'masks')
    fill(objs, 'objs')
    fill(objssig, 'objssigs')
    fill(objsmasks, 'objsmasks')
    fill(psfs, 'psfs')
    return data

def drop(name, val):
    import cPickle
    data = {}
    try:
        data = pick()
    except:
        pass
    f = open('param.dat', 'wb')
    data[name]=val
    cPickle.dump(data, f)
    f.close()

def pick(name=None, file='param.dat'):
    import cPickle
    pkl_file = open(file, 'rb')
    dic = cPickle.load(pkl_file)
    pkl_file.close()
    if name is None:
        return dic
    return dic[name]















    

