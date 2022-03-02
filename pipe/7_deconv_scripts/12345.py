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

# os.system(f"{python} 0_facult_autoskiplist_NU.py")
os.system(f"{python} 1_prepfiles.py")
os.system(f"{python} 2_applynorm_NU.py")
os.system(f"{python} 3_fillinfile_NU.py")
os.system(f"{python} 4_deconv_NU.py")
os.system(f"{python} 5b_showptsrc_NU.py")
os.system(f"{python} 5a_decpngcheck_NU.py")
