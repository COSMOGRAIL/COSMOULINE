
import numpy as np
import lib.utils as fn
import sys, string

def prompt(file=None):
    if file is None:
        file = 'gsig.fits'
        opt, args = fn.get_args(sys.argv)
        if args is not None: file = args[0]
    
    data = fn.get_data(file, '')
    fn.array2ds9(data, zscale=True)
    
    print 'Place markers on the desired region (only circles and polygons are supported).'
    sys.stdout.write('[Press ENTER when you are done (opt: enter the mask value)]')
    
    input = raw_input()
    if input == 'q' or input == 'quit':
        return 0
    mask = fn.get_ds9_mask(data.shape)
    
    try:
        val = eval(string.strip(input))
    except:
        val = 1.e10
        print 'Using default mask value:', val
    print (data*mask).sum()
    np.putmask(data, mask, val)
    fn.array2ds9(mask, frame=2, name='mask')
    fn.array2ds9(data, frame=3, name='new_data', zscale=False)
    fn.array2fits(data, file)
    
if __name__ == "__main__":
    sys.exit(prompt())
