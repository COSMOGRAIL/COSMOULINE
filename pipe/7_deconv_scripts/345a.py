from subprocess import call

import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import python

call([python, "3_fillinfile_NU.py"])
call([python, "4_deconv_NU.py"])
call([python, "5a_decpngcheck_NU.py"])

