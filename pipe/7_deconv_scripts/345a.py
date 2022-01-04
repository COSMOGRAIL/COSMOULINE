from subprocess import call

exec (open("../config.py").read())

call([python,  "3_fillinfile_NU.py"])
call([python, "4_deconv_NU.py"])
call([python, "5a_decpngcheck_NU.py"])

pngkey = deckey + "_png"
pngdir = os.path.join(workdir, pngkey)
os.system(f'xdg-open {pngdir}/00001.png')
