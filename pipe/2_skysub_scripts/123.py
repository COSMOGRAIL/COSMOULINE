import os
import sys
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')

from config import defringed, python, settings
from modules.variousfct import proquest

os.system(f"{python} 1_skysub_NU.py")

if defringed:
    os.system(f"{python} 1b_compute_fringes.py")

if settings['sample_only']:
    os.system(f"{python} 2_skypng_sample_NU.py")
else:
    os.system(f"{python} 2_skypng_NU.py")

print("I can remove the electron images.")
proquest(True)
os.system(f"{python} 3_facult_rm_electrons_NU.py")
