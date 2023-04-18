#
#    generates overview pngs related to the pyMCS psf construction
#    NEW : add a imgname to jpgnumber report,
#    to help the construction of the skiplist
#

import h5py
import numpy as np
import json
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import settings, psfstarcat, psfkey, psfsfile, psfsplotsdir,\
                   starsfile, noisefile, cosmicslabelfile, extracteddir
from modules import star, f2n


workdir = settings['workdir']
update = settings['update']
askquestions = settings['askquestions']
psfstars = settings['psfname']

pngdir = os.path.join(workdir, psfkey + "_png")
nbrpsf = len(psfstars)

regfile = extracteddir / 'regions.h5'


with open(cosmicslabelfile, 'r') as f:
    cosmicsdic = json.load(f)

def plot_psf(image, noise, lossplot):
    
    """
        image: database entry
        noise: array (npsfstars, shapex, shapey) the effective noisemap used in the deconv
        lossplot: 256x256 array containing a plot of the loss history
    """
    psfsplotsdir.mkdir(exist_ok=True, parents=True)
    imgname = image['imgname']
    
    # load all the stuff
    with h5py.File(psfsfile, 'r') as f:
        psf = np.array(f[imgname + '_narrow'])
        # numpsf = np.array(f[imgname + '_num'])
        residuals = np.array(f[imgname + '_residuals'])
        stars = np.array(f[imgname + '_data'])

    
    tilesize = 256
    imsizeup = psf[0].shape[0]
    imsize   = stars[0].shape[0]
    
    cosmicslist = [cosmicsdic[imgname + '_' + s] for s in psfstars]
            

        
    totpsfimg = f2n.f2nimage(psf, verbose=False)
    
    pngpath = os.path.join(psfsplotsdir, imgname + ".png")
    
    lossim = f2n.f2nimage(lossplot, verbose=False)
    lossim.setzscale(0, 255)
    lossim.makepilimage(scale="lin", negative=False)
    if tilesize != lossplot.shape[0]:
        lossim.upsample(tilesize/lossplot.shape[0])

    
    

    #totpsfimg.rebin(2)
    totpsfimg.setzscale('auto', 'auto')
    totpsfimg.makepilimage(scale="log", negative=False)
    totpsfimg.upsample(tilesize/imsizeup)
    totpsfimg.writetitle("Total PSF")
    
    # numpsfimg = f2n.f2nimage(numpsf, verbose=False)
    # numpsfimg.setzscale(-0.03, 0.8)
    # numpsfimg.makepilimage(scale = "lin", negative=False)
    # numpsfimg.upsample(tilesize/imsizeup)
    # numpsfimg.writetitle("Numerical PSF")
    
    
    
    
    txtendpiece = f2n.f2nimage(shape=(tilesize,tilesize), fill=0.0, verbose=False)
    txtendpiece.setzscale(0.0, 1.0)
    txtendpiece.makepilimage(scale = "lin", negative = False)
    
    date = image['datet']
    telname = "Telescope : %s" % image["telescopename"]
    # medcoeff = "Medcoeff : %.2f" % image["medcoeff"]
    seeing = "Seeing : %4.2f [arcsec]" % image['seeing']
    ell = "Ellipticity : %4.2f" % image['ell']
    # nbralistars = "Nb alistars : %i" % image['nbralistars']
    airmass = "Airmass : %4.2f" % image['airmass']
    az = "Azimuth : %6.2f [deg]" % image['az']
    stddev = "Sky stddev : %4.2f [ADU]" % image['prealistddev']
    skylevel = "Sky level : %7.1f [ADU]" % image['skylevel']
    # we write long image names on two lines ...
    if len(image['imgname']) >= 27:
        infolist = [image['imgname'][0:20]+"...", "   "+image['imgname'][20:]]
    else:
        infolist = [image['imgname']]
    infolist.extend([date, telname, seeing, ell, \
                     stddev, skylevel, airmass, az])
    if settings['thisisatest']:
        testcomment = 'Testcomment: %s' %image['testcomment']
        infolist.append(testcomment)
    txtendpiece.writeinfo(infolist)
    
    
    # The psf stars
    psfstarimglist = []
    for j in range(nbrpsf):
        f2nimg = f2n.f2nimage(stars[j], verbose=False)
        f2nimg.setzscale("auto", "auto")
        f2nimg.makepilimage(scale = "log", negative = False)
        f2nimg.upsample(tilesize/imsize)
        f2nimg.drawstarlist(cosmicslist[j], r=3)
        f2nimg.writetitle("%s" % (psfstars[j]))
        psfstarimglist.append(f2nimg)
    
    psfstarimglist.append(txtendpiece)

    
    
    # The sigmas
    sigmaimglist = []
    for j in range(nbrpsf):
        
        noise[j][np.where(noise[j]>1e1)] = 0.2
        f2nimg = f2n.f2nimage(noise[j], verbose=False)
        f2nimg.setzscale('auto', 'auto')
        f2nimg.makepilimage(scale = "log", negative=False)
        f2nimg.upsample(tilesize/imsize)
        f2nimg.writetitle('noise map')
        #f2nimg.drawstarlist(cosmicslist, r=10)
        #f2nimg.writetitle("%s" % (psfstars[j].name))
        sigmaimglist.append(f2nimg)
    
    sigmaimglist.append(lossim)
    
    # The residuals
    difnumlist = []
    for j in range(nbrpsf):
        
        
        f2nimg = f2n.f2nimage(residuals[j]/noise[j], verbose=False)
        f2nimg.setzscale('auto', 'auto')
        f2nimg.makepilimage(scale = "lin", negative = False)
        f2nimg.upsample(tilesize/imsize)
        #f2nimg.writeinfo([image['imgname']], (255, 0, 0))
        #f2nimg.writeinfo(["","g001.fits"])
        f2nimg.writetitle("rel. residuals")
        difnumlist.append(f2nimg)
    
    difnumlist.append(totpsfimg)

        

    f2n.compose([psfstarimglist, sigmaimglist, difnumlist], pngpath)    


