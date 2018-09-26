import os

execfile("../config.py")
from variousfct import *

os.system("python 1_skysub_NU.py")
if defringed:
    os.system("python 1b_compute_fringes.py")

if sample_only :
    os.system("python 2_skypng_sample_NU.py")
else:
    os.system("python 2_skypng_NU.py")

print "I can remove the electron images."
proquest(True)
os.system("python 3_facult_rm_electrons_NU.py")
