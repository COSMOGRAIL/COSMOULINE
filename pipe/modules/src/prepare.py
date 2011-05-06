import sys
import lib.utils as fn
import lib.wsutils as ws

def main(argv=None):
    out = fn.Verbose()
    cfg = 'config.py'
    if argv is not None:
        sys.argv = argv
    opt, args = fn.get_args(sys.argv)
    CLEAN = EXTRACT = BACKUP = VERBOSE = DEBUG = SILENT = False
    if 'c' in opt: 
        CLEAN = True
    if 'b' in opt: 
        BACKUP = True
    if 'e' in opt: 
        EXTRACT = True
    if 's' in opt: 
        SILENT = True
        out.level = 0
    if 'v' in opt: 
        VERBOSE = True
        out.level = 2
    if 'd' in opt: 
        DEBUG = True
        out.level = 3
        out(1, '~~~ DEBUG MODE ~~~')
    if 'h' in opt:
        out(1, 'No help page yet!')
        return 0
    out(1, 'Begin workspace preparation...')
    if args is not None: cfg = args[0]
    out(2, 'Setting up workspace layout...')
    ws.setup_workspace()
    if BACKUP is True:
        out(2, 'Backing up old files and '+cfg+' configuration file...')
        ws.backup_workspace(cfg)
    if CLEAN is True:
        out(2, 'Cleaning up workspace (delete all .fits files in results/)...')
        ws.clean_workspace()
    if EXTRACT is True:
        out(2, 'Extracting all images...')
        f = open(cfg, 'r')
        exec f.read()
        f.close()
        vars = ['FILENAME', 'STARS', 'NPIX', 'OBJ_POS', 
                'OBJ_SIZE', 'IMG_GAIN', 'SKY_BACKGROUND', 
                'SIGMA_SKY', 'IMG_GAIN']
        err = fn.check_namespace(vars, locals())
        if err > 0:
            return 1
        ws.populate(FILENAME, STARS, NPIX, OBJ_POS, OBJ_SIZE, 
                    SKY_BACKGROUND, SIGMA_SKY, IMG_GAIN, clean = 0)
    out(1, 'Done, exiting prepare.py')
    return 0
    
    
if __name__ == "__main__":
    sys.exit(main())