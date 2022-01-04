import os

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from variousfct import *

os.system(f"{python} 1_skysub_NU.py")
if defringed:
    os.system(f"{python} 1b_compute_fringes.py")

if sample_only :
    os.system(f"{python} 2_skypng_sample_NU.py")
else:
    os.system(f"{python} 2_skypng_NU.py")

print("I can remove the electron images.")
proquest(True)
os.system(f"{python} 3_facult_rm_electrons_NU.py")
