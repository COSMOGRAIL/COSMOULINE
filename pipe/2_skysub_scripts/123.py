import os

execfile("../config.py")
os.system("python 1_skysub_NU.py")
if sample_only :
    os.system("python 2_skypng_sample_NU.py")
else:
    os.system("python 2_skypng_NU.py")
os.system("python 3_facult_rm_electrons_NU.py")
