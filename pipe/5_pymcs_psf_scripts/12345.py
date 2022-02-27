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

os.system(f'{python} 1_prepare.py')
os.system(f'{python} 2a_extract_NU.py')
os.system(f'{python} 2b_facult_applymasks_NU.py')
os.system(f'{python} 3_facult_findcosmics_NU.py')
os.system(f'{python} 4_buildpsf_NU.py')
os.system(f'{python} 5_pngcheck_NU.py')
