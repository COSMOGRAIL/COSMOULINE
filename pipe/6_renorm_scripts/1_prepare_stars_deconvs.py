#    
#    Do the deconvolution of all stars: one point source.
#
import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))

sys.path.append('..')


from config import settings
from modules.prepare_deconvolution import prepare_deconvolution


renorm_stars = settings['renorm_stars']
decname = settings['decname']
decnormfieldname = settings['decnormfieldname']

if not decname == 'noback' or not decnormfieldname == 'None':
    print("Your decname is not 'noback' or your decnormfieldname is not 'None'.")
    print("Please make set them this way to be consistent with the COSMOULINE tradition.")
    print("Also, during the normalization we will looks for deconvs named `noback`.")
    sys.exit()

for star in renorm_stars:
    # norm coefficient: 1 everywhere
    prepare_deconvolution(star, decnormfieldname="None") 
