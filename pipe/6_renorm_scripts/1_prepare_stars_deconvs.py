#    
#    Do the deconvolution of all stars: one point source.
#
import sys
import os

# if ran as a script, append the parent dir to the path
sys.path.append(os.path.dirname(sys.path[0]))

sys.path.append('..')

from config import settings
from modules.prepare_deconvolution import prepare_deconvolution

renorm_stars = settings['renorm_stars']

for star in renorm_stars:
    # norm coefficient: 1 everywhere
    prepare_deconvolution(star, decnormfieldname="None", decname="noback")
