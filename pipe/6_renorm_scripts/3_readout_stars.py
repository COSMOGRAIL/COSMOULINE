import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')


    

from config import settings
from modules.deconv_utils import readout_object


norm_stars = settings['norm_stars']

for star in norm_stars:
    readout_object(star, decname="noback", decnormfieldname="None")