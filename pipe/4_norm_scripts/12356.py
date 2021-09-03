import os

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

os.system("python3 1a_imstat.py")
os.system("python3 1b_facult_multicpu_fillnoise_NU.py")
os.system("python3 2a_runsex_NU.py")
os.system("python3 2b_facult_photomdb.py")
os.system("python3 2c_facult_peakdb.py")
os.system("python3 2d_facult_plotpeakadu_NU.py")
os.system("python3 3a_calccoeff.py")
os.system("python3 3b_report_NU.py")
os.system("python3 3c_plotphotomstars_NU.py")
os.system("python3 5_histo_multifield_NU.py")
os.system("python3 6_facult_merge_pdf_NU.py")