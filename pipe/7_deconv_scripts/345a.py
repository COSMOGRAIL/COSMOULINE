import os

exec (open("../config.py").read())
os.system("python3 3_fillinfile_NU.py")
os.system("python3 4_deconv_NU.py")
os.system("python3 5a_decpngcheck_NU.py")

