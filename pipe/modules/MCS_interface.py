import os, cPickle, copy
from src import prepare, _1_get_sky, set_mask, _2_get_stars, _3_fitmof
from src import _4_fitgaus, _4b_fitnum, _5_PSFgen, deconv_simult, get_ini_par
import src.lib.wsutils as ws
import src.lib.utils as fn

out = fn.Verbose()


class MCS_interface():
    
    def __init__(self, cfg_file='config.py'):
        self.cfg = cfg_file
        self.ready = False
        self.params = {}
        self.data = {}
        self.needed_par = ['FILENAME', 'STARS', 'NPIX', 'OBJ_POS', 'OBJ_SIZE', 'IMG_GAIN', 'SKY_BACKGROUND', 
                           'SIGMA_SKY', 'IMG_GAIN', 'NBINS', 'SKY_RANGE', 'SHOW', 'G_RES', 'MAX_IT', 'S_FACT',
                           'MOF_INIT', 'G_RES', 'G_STRAT', 'G_SETTINGS', 'FIT_RAD', 'NB_RUNS', 'PSF_SIZE',
                           'MOF_PARAMS', 'MAX_IT_D', 'G_PARAMS', 'G_POS', 'MAXPOS_RANGE', 'MAX_IRATIO_RANGE', 
                           'FORCE_INI', 'SRC_PARAMS', 'IMG_OFFSETS', 'MAX_IT_N', 'LAMBDA_NUM', 'BKG_STEP_RATIO_NUM',
                           'CUDA', 'BKG_INI_CST', 'BKG_STEP_RATIO', 'BKG_START_RATIO', 'LAMBDA','NB_SRC','BOX_SIZE',
                           'SRC_RANGE', 'D_NB_RUNS', 'USE_MOMENTS', 'NOBJ', 'VAL_BND', 'NOWRITE', 'INI_PAR',
                           'FFT_DIV', 'CENTER', 'PSF_RAD']
        self.check_workspace()
        self.emerge()

    def __dir__(self):
        return self.listop()

    def help(self):
        print 'help page in construction'
        self.listop()
        
    def listop(self):
        """
        List all available operations. Display the operations and return a list with the methods signatures.
        
        @rtype: list
        @return: List of available methods
        """
        attr = self.__dict__.keys()
        l = [e for e in dir(self) if ('__' not in e) and (e not in attr)]
        out(1, 'Available operations:')
        for op in l:
            out(2, op)
        return l
    
    def check_cfg_val(self):
        """
        """
        return True
        
    def check_workspace(self):
        """
        Check the workspace structure and restore the standard 
        layout if needed. Includes the check of available modules 
        and the class' parameters initialization.
        
        @rtype: boolean
        @return: State of the workspace. True if all is OK, False if \
                 something's not right (should run set_up_workspace in that case).
        """
        ws.setup_workspace()
        f = open(self.cfg, 'r')
        exec f.read()
        f.close()
        err = fn.check_namespace(self.needed_par, locals())
        if len(err)>0: 
            raise EnvironmentError, 'Parameters problem. Needs:'+ str(err)
        for p in self.needed_par:
            self.params[p] = eval(p)
        while not self.check_cfg_val():
            out(2, 'Bad parameters values. Please change and press ENTER','-r')
            _ = raw_input()
        files, cat = ws.get_files(FILENAME, directory='images')
        self.params['filenb'] = len(files)
        self.params['img_names'] = files
        self.params['starnb'] = len(self.params['STARS'])
        self.data = ws.restore(*ws.getfilenames(self.params['filenb']))
        #TODO: add consistency checks
#        if len(self.params['stars']) != self.params['starnb']:
#            return False
        return True
    
    def set_up_workspace(self, extract=True, clear=False, backup=False):
        """
        Create the default layout of the workspace
        
        @type extract: boolean
        @param extract: True for extracting (overwrite) the images (default: True)
        @type clear: boolean
        @param clear: True for erasing every .fits image in the results folder (default: False)
        @type backup: boolean
        @param backup: True for backing up the .fits images in the results folder, \
                       as well as the configuration file   (default: False)
        """
        if backup:
            out(2, 'Backing up old files and '+self.cfg+' configuration file...')
            ws.backup_workspace(self.cfg)
        if clear:
            out(2, 'Cleaning up workspace (delete all .fits files in results/)...')
            ws.clean_workspace()
        if extract:
            self.refresh()
            out(2, 'Extracting all images...')
            ws.populate(self.params['FILENAME'], self.params['STARS'], self.params['NPIX'], 
                        self.params['OBJ_POS'], self.params['OBJ_SIZE'], self.params['SKY_BACKGROUND'], 
                        self.params['SIGMA_SKY'], self.params['IMG_GAIN'], clean = 0)
        self.ready = self.check_workspace()
#        opt = '-' + 'e'*extract + 'c'*clear + 'b'*backup
#        prepare.main(['MCS_interface.py', opt, self.cfg])
    
    def emerge(self):
        """
        Restore all the parameters from the files.
        
        Look at the check_workspace method for more details.
        """
        self.check_workspace()
#        self.params = ws.pick()
        self.save()
        self.ready = True
    
    def hibernate(self):
        """
        Save everything to the disk, such that we may restart \
        from the same point the next time emerge is called.
        
        """
        self.save(all=True)
    
    def refresh(self):
        """
        Refresh the attributes and parameters with the stored values.
        
        Look at the check_workspace method for more details.
        """
        self.check_workspace()
    
    def save(self, all=False):
        """
        Save the attributes and parameters, including the images if 'all' is True.
        The keywords from the 'needed_par' class attribute are saved \
        in the parameter file and the 'param.dat' file is updated.
        
        @type all: boolean
        @param all: True for saving the .fits images (default: False)
        """
        d = {}
        for e in self.needed_par:
            d[e] = self.params[e]
        fn.write_cfg(self.cfg, d)
        f = open('param.dat', 'wb')
        cPickle.dump(self.params, f)
        f.close()
        if all:
            #TODO: save the images
            pass
    
    def get_sky(self):
        """
        Compute the sky value of the image(s).
        
        An histogram of the pixels' value is built and a gaussian is fitted over it.
        The sky value corresponds to the center of the gaussian, while the sigma of the sky corresponds to the width.
        
        Save the results in a list, one value for each of the images.
        Update the configuration file keywords SKY_BACKGROUND and SIGMA_SKY
        """
        self.refresh()
        fnb = self.params['filenb']
        skyl = []
        sigl = []
        for i in xrange(fnb):
            f = self.params['img_names'][i]
            out(1, '===============', i+1, '/', fnb,'===============|')
            out(1, 'Getting sky from', f)
            sky, sig = _1_get_sky.get_sky_val(fn.get_data(f, directory='images'), show = self.params['SHOW'], 
                                              range=self.params['SKY_RANGE'], nbins=self.params['NBINS'])
            skyl += [sky]
            sigl += [sig]
            out(1, 'Analysis done! Sky:', sky, 'sigma:', sig)
        self.params['SKY_BACKGROUND'] = skyl
        self.params['SIGMA_SKY'] = sigl
        self.save()
    
    def get_stars(self, interactive=False):
        """
        Call the procedure getting the stars positions.
        
        @type interactive: boolean
        @param interactive: True to enable the interactive mode (default: False).
        
        If the interactive mode is on, the positions of the stars will be acquired \
        by prompting the user for ds9 regions.
        If not, the program will attempt to find stars by looking at different objects\
        and choosing those with correlated ellipticities. Those are found by fitting a gaussian \
        or by looking at the 2nd order moments (USE_MOMENTS keyword of the configuration file).
        """
        self.refresh()
        files, cat = ws.get_files(self.params['FILENAME'], directory='images')
        img = fn.get_data(files[0], 'images')
        if interactive:
            fn.array2ds9(img, zscale=True)
            out(1, 'Place markers on the desired stars (may not work if several ds9 instances are actives).')
            out(1, '[Press ENTER when you are done]', '-r')
            _ = raw_input()
            stars = []
            for r in _2_get_stars.getregions():
                stars += [(r.x,r.y)]
            out(1, stars)
        else:
            stars, candidates = _2_get_stars.get_stars(img, self.params)  
        if self.params['NOWRITE'] is False:
            self.params['STARS'] = stars
            self.save()
    
    def put_masks(self, file='gsig.fits'):
        """
        Interactively put a mask over the file in argument (default: gsig.fits) 
        
        @type file: string
        @param file: Name of the image to modify (sigma). Should be in the 'results' folder\
                     (default: gsig.fits).
        """
        f = os.path.join('results',file)
        set_mask.prompt(os.path.join(os.getcwd(),f))
        
    def create_image(self):
        """
        Call the image generator procedure
        """
        import src.artif_img_creator
        src.artif_img_creator.main()
        
    def fitmof(self):
        """
        Fit a Moffat profile over the stars
        """
        self.refresh()
        fnb = self.params['filenb']
        mpar = []
        out(1, 'Begin moffat fit')
        for i in xrange(fnb):
            f = self.params['img_names'][i]
            out(1, '===============', i+1, '/', fnb,'===============|')
            out(1, 'Working on', f)
            mofpar, r = _3_fitmof.fitmof(i, self.data, self.params)
            mpar += [mofpar.tolist()]
        out(1, 'Moffat fit done')
        self.params['MOF_PARAMS'] = mpar
        self.save()
        
    def fitnum(self):
        """
        Fit a background model over the residuals of the Moffat fit
        """
        self.refresh()
        fnb = self.params['filenb']
        out(1, 'Begin numerical fit')
        for i in xrange(fnb):
            f = self.params['img_names'][i]
            out(1, '===============', i+1, '/', fnb,'===============|')
            out(1, 'Working on', f)
            _4b_fitnum.fitnum(i, self.data, self.params)
        out(1, 'Numerical fit done')
        self.save() #not needed (a priori)

    def fitgaus(self):
        """
        Fit gaussians on the residuals of the Moffat fit
        """
        self.refresh()
        fnb = self.params['filenb']
        gpar = []
        gpos = []
        out(1, 'Begin gaussian fit')
        for i in xrange(fnb):
            f = self.params['img_names'][i]
            out(1, '===============', i+1, '/', fnb,'===============|')
            out(1, 'Working on', f)
            gauspar, gauspos = _4_fitgaus.fitgaus(i, self.data, self.params)
            gpar += [gauspar]
            gpos += [gauspos]
        out(1, 'Gaussian fit done')
        self.params['G_PARAMS'] = gpar
        self.params['G_POS'] = gpos
        self.save() 
    
    def psf_gen(self):
        """
        Generate the analytical PSF 
        """
        self.refresh()
        fnb = self.params['filenb']
        for i in xrange(fnb):
            out(1, 'Generate PSF', i+1)
            _5_PSFgen.psf_gen(i, self.params)
        out(1, 'Done')

    def deconv_ini(self):
        """
        Get the initial parameters for the deconvolution
        """
        self.refresh()
        out(1, 'Begin parameters initialization')
        bkg, src, shifts = get_ini_par.set_ini(self.data, self.params)
        out(1, 'Parameters initialization done')
        self.params['INI_PAR'] = src.ravel().tolist()
        self.params['IMG_OFFSETS'] = shifts.tolist()
        fn.array2fits(bkg, 'results/bkg_ini.fits')
        self.save() 
        
    def get_src_par(self):
        par = array(self.params['SRC_PARAMS'])
        par.shape = len(par)//3, 3
        return par.tolist()
        
    def set_src_par(self, par):
        self.params['SRC_PARAMS'] = fn.flatten(par)
        self.save()
        
    def deconvolve(self):
        """
        Deconvolve the data
        """
        self.refresh()
        out(1, 'Begin deconvolution')
        src_params, offsets, srcini = deconv_simult.deconv(self.data, self.params)
        out(1, 'Deconvolution done')
        self.params['SRC_PARAMS'] = src_params.tolist()
        self.params['IMG_OFFSETS'] = offsets
        self.params['INI_PAR'] = srcini.tolist()
        self.save() 

    def switch_ini(self):
        """
        Switch the deconvolution initial parameters with the new ones
        """
        self.refresh()
        self.params['INI_PAR'] = copy.deepcopy(self.params['SRC_PARAMS'])
        bk = fn.get_data('bkg.fits')
        fn.array2fits(bk,  os.path.join('results','bkg_ini.fits'))
        self.save()
        out(2, 'Parameters switched')





