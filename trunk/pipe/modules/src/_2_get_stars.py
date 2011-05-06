  
import numpy as np
from lib.Candidate import Candidate
import lib.utils
import sys
import lib.wsutils as ws
import lib.utils as fn

out = fn.Verbose()

def __print_stars(clist, smax, sig, out=True, save=None, data=None, imgw=None):
    #TODO: set the scale correctly for each graph
    import pylab
    global rejected, texts
    nx = int(np.sqrt(smax))
    ny = nx + 2
    i = 1
    im1 = []
    im2 = []
    im3 = []
    im4 = []
    im5 = []
    rejected = []
    texts = []
    slist = []
    pylab.figure(1)
    for c in clist:
        if c.grade > 2:
            print c
            slist += [c]
            pylab.subplot(nx,ny,i)
            pylab.title('candidate '+str(i))
            extent = (0,c.img.shape[1],0,c.img.shape[0])
            im1 += [pylab.imshow(c.img, extent=extent, interpolation="nearest")]
            im2 += [pylab.imshow(c.chi, extent=extent, hold=True, interpolation="nearest")]
            pylab.colorbar(im2[-1])
            im2[-1].set_visible(False)
            if sig is not None:
                chisig1 = c.chi.copy()
                chisig2 = c.chi.copy()
                chisig3 = c.chi.copy()
                chisig1[np.where(abs(chisig1)>sig)] = 0.
                chisig2[np.where(abs(chisig2)>2.*sig)] = 0.
                chisig3[np.where(abs(chisig3)>3.*sig)] = 0.
                im3 += [pylab.imshow(chisig1, extent=extent, hold=True, interpolation="nearest")]
                im4 += [pylab.imshow(chisig2, extent=extent, hold=True, interpolation="nearest")]
                im5 += [pylab.imshow(chisig3, extent=extent, hold=True, interpolation="nearest")]
                im3[-1].set_visible(False)
                im4[-1].set_visible(False)
                im5[-1].set_visible(False)
            i += 1
    def toggle_images(event):
        key = event.key
        keys = '0'
        if sig is not None:
            keys = '1230'
        b1 = im1[0].get_visible() 
        b2 = im2[0].get_visible() or b1==False
        if key not in keys: 
            return
        for im in im1:
            im.set_visible(not b1 and key=='0')
        for im in im2:
            im.set_visible(not b2 and key=='0')
        if sig is not None:
            for im in im3:
                im.set_visible(key=='1')
            for im in im4:
                im.set_visible(key=='2')
            for im in im5:
                im.set_visible(key=='3')
        pylab.draw()
    def click(event):
        canvas = event.canvas        
        if event.inaxes and event.xdata>1. and event.ydata>1.:
            global rejected, texts
            for i, ax in enumerate(rejected):
                if event.inaxes is ax:
                    event.inaxes.texts.remove(texts[i])
                    del rejected[i]
                    del texts[i]
                    break

            else:
                texts += [event.inaxes.annotate('REMOVED', xy=(1, 1), color='red')]
                rejected += [event.inaxes]
        pylab.draw()
    pylab.connect('key_press_event', toggle_images)
    pylab.connect('button_press_event', click)
    if save != None:
        import lib.AImage, ImageDraw, Image
        #from PIL import Image
        split=save.split('.')
        ext = '.' + split[-1]
        del split[-1]
        base = ''
        for s in split:
            base += s + '.'
        if base[-1] == '.': base = base[:-1]
        split = save.split('/')[0:-1]
        dir = ''
        for s in split:
            dir += s + '/'
        pylab.savefig(save)
        for im in im2:
            im.set_visible(True)
        for im in im1:
            im.set_visible(False)
        pylab.savefig(base+'_sig'+ext)
        for im in im3:
            im.set_visible(True)
        for im in im2:
            im.set_visible(False)
        pylab.savefig(base+'_1sig'+ext)
        for im in im4:
            im.set_visible(True)
        for im in im3:
            im.set_visible(False)
        pylab.savefig(base+'_2sig'+ext)
        for im in im5:
            im.set_visible(True)
        for im in im4:
            im.set_visible(False)
        pylab.savefig(base+'_3sig'+ext)
        img = makepilimage(lib.AImage.Image(data))
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        for c in clist:
            if c.grade > 2:
                draw.text((c.x, c.y-c.rad[0]-10), str(c.id), fill="#00ff00")
                draw.ellipse([(c.x-c.rad[0], c.y-c.rad[1]), (c.x+c.rad[1], c.y+c.rad[0])], outline="#00ff00")
            else:
                draw.ellipse([(c.x-c.rad[0], c.y-c.rad[1]), (c.x+c.rad[1], c.y+c.rad[0])], outline=(255,0,0))#"#ff0000")
                draw.text((c.x, c.y-c.rad[0]-10), str(c.id), fill="#ff0000")
            r = max(c.rad)+10
            thumb = img.crop((c.x-r, c.y-r,c.x+r, c.y+r))
            thumb = thumb.resize((128,128), Image.ANTIALIAS)
            thumb.save(dir+'thumb/candidate_'+str(c.id)+'.png', "PNG")
        del draw
        if imgw is not None:
            low = img.resize((imgw,img.size[1]*imgw/img.size[0]), Image.ANTIALIAS)
            low.save(base+'_img_low.png', "PNG")
        img.save(base+'_img.png', "PNG")
    if out == True:
        pylab.show()
    final_slist = []
    for i, im in enumerate(im1):
        for ax in rejected:
            if ax is im.get_axes():
                break
        else:
            final_slist += [slist[i]]
    pylab.clf()
    return final_slist
    
    
def __get_clist(img, nobj, sky, sigma, gain, val_bnd, usemom):
    mask = np.zeros(img.shape) + 1
    img[np.isnan(img)]= sky
    data = img.copy()
    #mask[1300:2000, 1200:1350] = 0
    #mask[:1200, 960:965] = 0.
    #mask[:, 0:120] = 0
    candidate_list = []
    print "Acquiring candidates positions..."
    n = 0
    while n < nobj:
        x, y = divmod(data.argmax(), data.shape[1])
        max_val = data[x,y]
        if max_val <= 0. or (val_bnd is not None and val_bnd != (0,0) and max_val <= val_bnd[0]):
            print "exiting, max candidates number reached:", n
            break
        c = Candidate(x,y)
        if val_bnd is not None and val_bnd != (0,0) and (max_val > val_bnd[1] or max_val < val_bnd[0]):
            ind = c.get_rad(data, mask)
            mask[c.x-ind[0]:c.x+ind[1],c.y-ind[2]:c.y+ind[3]] = 0
            data[c.x-ind[0]:c.x+ind[1],c.y-ind[2]:c.y+ind[3]] = sky
        else:
            bad = c.set_param(data, mask, sigma, gain, sky, usemom)
            if bad: break
            if not np.isnan(c.get_par()).any():
                candidate_list += [c]
                #TODO: out(...)
                sys.stdout.write("\rcandidates found: " + str(n+1)+ "         ")
                sys.stdout.flush()
                n += 1
    return candidate_list

def __clean_ell(c_list):
    cleaned = []
    med = []
    for c in c_list:
        med += [c.e]
    med = np.median(med)
    for c in c_list:
        if c.e < 3. * med:
            cleaned += [c]
    return cleaned, len(c_list) - len(cleaned) 

def get_stars(data, params, imgw=None):
    nobj, sky, sigma = params['NOBJ'],params['SKY_BACKGROUND'][0],params['SIGMA_SKY'][0]
    gain, upper, out, save = params['IMG_GAIN'],params['VAL_BND'],params['SHOW'], None
    usemom = params['USE_MOMENTS']
    
    candidate_list = __get_clist(data, nobj, sky, sigma, gain, upper, usemom)
    e_list = []
    rot_list = []
    fwhm_list = []
    print "Checking abnormal ellipticities..."
    candidate_list, bad = __clean_ell(candidate_list)
    print "\n", bad, "candidate(s) removed due to a bad ellipticity"
    for i, c in enumerate(candidate_list):
        c.id = i+1
        e_list += [c.e]
        rot_list += [c.rot]
        fwhm_list += [c.fwhm]
        
    smax, chlog = 0, [0,0]
    for binv in xrange(4):
        fbins = 10
        erbins = 10
        if binv == 0 and out == True:
            print "\nBegin candidates selection (checking ellipticity-rotation-fwhm correlations):"
        elif binv == 1:
            fbins = 12
            print smax, "candidate(s) remaining.", "Variating bins width 1..."
        elif binv == 2: 
            if chlog[0] == 1:
                fbins = 12
            erbins = 12
            print smax, "candidate(s) remaining.", "Variating bins width 2..."
        elif binv == 3:
            if chlog == (0,0):
                break
            else:
                fbins = 10 + chlog[0]*2
                erbins = 10 + chlog[1]*2     
        hg_e = np.histogram(e_list, bins=erbins, normed=False)
        hg_r = np.histogram(rot_list, bins=erbins, normed=False)
        hg_f = np.histogram(fwhm_list, bins=fbins, normed=False)
        print hg_e
        for c in candidate_list:
            c.grade = 1
        hlist = []
        ilist = []
        for i in xrange(hg_e[0].shape[0]):
            #i = np.where(hg[0] == hg_e[0].max())[0][0]
            up, down = hg_e[1][i+1], hg_e[1][i]
            rlist = []
            for c in candidate_list:
                if c.e >= down and c.e <= up:
                    rlist += [c.rot]
            h = np.histogram(rlist, bins=hg_r[1], normed=False)[0]
            ilist += [np.where(h == h.max())[0][0]]
            hlist += [h.max()]
        bin_e = np.where(hlist == max(hlist))[0][0]
        bin_rot = ilist[bin_e]

        e0, e1 = hg_e[1][bin_e], hg_e[1][bin_e+1]
        r0, r1 = hg_r[1][bin_rot], hg_r[1][bin_rot+1]
        flist = []
        for c in candidate_list:
            if c.e >= e0 and c.e <= e1 and c.rot >= r0 and c.rot <= r1:
                c.grade += 1
                flist += [c.fwhm]
        h = np.histogram(flist, bins=hg_f[1], normed=False)[0]
        bin_fwhm = np.where(h == h.max())[0][0]
        grade3_list = []
        for c in candidate_list:
            if c.fwhm >= hg_f[1][bin_fwhm] and c.fwhm <= hg_f[1][bin_fwhm+1]:
                c.grade += 1
            if c.grade == 3:
                grade3_list += [c]
#                poslist += [(c.x, c.y)]
        l = len(grade3_list)
        if binv == 0:
            smax = l
        elif binv == 1 and l > smax:
            smax = l
            chlog[0] = 1
        elif binv == 2 and l > smax:
            smax = l
            chlog[1] = 1
    print "**************** Histograms ***************"
    print "hg_e:", hg_e
    print "hg_r:", hg_r
    print "hg_f:", hg_f
    print "****************** Stars ******************"
    print smax, "suitable stars found (grade 3):"
    slist = __print_stars(candidate_list, smax, sigma, out, save, data, imgw)
    poslist = []
    for s in slist:
        poslist += [(s.x, s.y)]
    print "Final stars' positions:", poslist
    return poslist, candidate_list


class marker:
    """
    Defines a class for storing SAO(tng/ds9) regions. Should work with any\
    type that defined by x, y, and size (eg circle), only tested for points.\
    Create an instance with:  m=xpa.marker(123.4, 345.6, 'lens'), for example.
         
    credits:
    http://internal.physics.uwa.edu.au/~andrew/AP7/xpa.py
    """
    def __init__(self,x=0,y=0,label='',type='point',size=0):
        self.x=x
        self.y=y
        self.label=label
        self.type=type
        self.size=size
    def display(self):   #Sends an XPA message to the viewer to show this marker
        if self.type=='point':  #Points don't have a size attribute
            cmd="regions '"+self.type+" "+`self.x`+" "+`self.y`+" # text={"+self.label+"} '"
            commands.getoutput('echo '+cmd+' | xpaset '+viewer)
        print cmd


def getregions():
    """
    Ask the viewer what regions are defined, parse the output, and \
    return a list of marker objects.
    
    credits:
    http://internal.physics.uwa.edu.au/~andrew/AP7/xpa.py
    """
    import commands
    import string
    import os
    out=string.split(commands.getoutput('xpaget ds9 regions'),'\n')
    label=''
    mlist=[]
    for r in out:       #For each line
        if r[0]=='#' or r[:6]=='global' or r[:3]=='XPA' or r[:8]=='physical':
            pass
        else:
            sc=string.find(r,';')
            ob=string.find(r,'(')
            cb=string.find(r,')')
            type=r[sc+1:ob]     #type is the string between the ; and the (
            ocb=string.find(r,'{')
            ccb=string.find(r,'}')
            label=r[ocb+1:ccb+1]   #The label is between curly brackets
            if type=='point':
                x,y=eval(r[ob+1:cb])  #Grab the X and Y values for a point
                m=marker(x,y,label,type)  #Create a marker object
            else:
                x,y,size=eval(r[ob+1:cb]) #Grab X,Y, and Size for a circle, etc
                m=marker(x,y,label,type,size)  #Create a marker object
            mlist.append(m)   #Add the object to the list
    return mlist


def main(argv=None):
    cfg = 'config.py'
    if argv is not None:
        sys.argv = argv
    opt, args = fn.get_args(sys.argv)
    p = interactive = False
    if args is not None: cfg = args[0]
    if 's' in opt: 
        out.level = 0
    if 'v' in opt: 
        out.level = 2
    if 'd' in opt: 
        DEBUG = True
        out.level = 3
        out(1, '~~~ DEBUG MODE ~~~')
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    if 'i' in opt:
        interactive = True
    VAL_BND = (0,0)
    USE_MOMENTS = False
    f = open(cfg, 'r')
    exec f.read()
    f.close()
    vars = ['FILENAME','SHOW', 'NOBJ','SKY_BACKGROUND',
            'SIGMA_SKY', 'IMG_GAIN', 'NOWRITE']
    err = fn.check_namespace(vars, locals())
    if err > 0:
        return 1
    #TODO: implement option choice
    files, cat = ws.get_multiplefiles(FILENAME, directory='img')
    
    out(2, FILENAME, cfg)
    data = lib.utils.get_data(files[0], 'img') #- SKY_BACKGROUND
    
    if interactive:
#        import numdisplay
        fn.array2ds9(data, zscale=True)
#        numdisplay.readcursor()
        out(1, 'Place markers on the desired stars (may not work if several ds9 instances are actives).')
        out(1, '[Press ENTER when you are done]', '-r')
        _ = raw_input()
        stars = []
        for r in getregions():
            stars += [(r.x,r.y)]
        out(1, stars)
    else:
        stars, candidates = get_stars(data, NOBJ, SKY_BACKGROUND[0], SIGMA_SKY[0], IMG_GAIN, VAL_BND, True, None, USE_MOMENTS)
    if NOWRITE is False:
        lib.utils.write_cfg(cfg, {'STARS':stars})
    return 0
    
    
if __name__ == "__main__":
#    import cProfile, pstats
#    prof = cProfile.Profile()
#    prof = prof.runctx("main()", globals(), locals())
#    stats = pstats.Stats(prof)
#    stats.sort_stats("time")  # Or cumulative
#    stats.print_stats(15)  # how many to print
    sys.exit(main())
