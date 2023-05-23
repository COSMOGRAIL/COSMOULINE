import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
    

    

from config import imgdb, settings, computer, deconvexe
from modules.variousfct import proquest, notify, nicetimediff
from modules.kirbybase import KirbyBase
from modules.prepare_deconvolution import prepare_deconvolution
from modules.deconv_utils import importSettings, readout_object


renorm_stars = settings['renorm_stars']

for star in renorm_stars:
    readout_object(star)