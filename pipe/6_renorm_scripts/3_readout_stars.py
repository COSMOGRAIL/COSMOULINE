import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
sys.path.append('..')


    

from config import settings
from modules.deconv_utils import readout_object


renorm_stars = settings['renorm_stars']

for star in renorm_stars:
    readout_object(star)