import os

exec (open("../config.py").read())
os.system("python 3_fillinfile_NU.py")
os.system("python 4_deconv_NU.py")
os.system("python 5a_decpngcheck_NU.py")

pngkey = deckey + "_png"
pngdir = os.path.join(workdir, pngkey)
os.system(f'xdg-open {pngdir}')
