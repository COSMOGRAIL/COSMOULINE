import os
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

os.system(f"{python} 1a_imstat.py")
os.system(f"{python} 1b_facult_multicpu_fillnoise_NU.py")
os.system(f"{python} 2a_runsex_NU.py")
os.system(f"{python} 2b_facult_photomdb.py")
os.system(f"{python} 2c_facult_peakdb.py")
os.system(f"{python} 2d_facult_plotpeakadu_NU.py")
os.system(f"{python} 3a_calccoeff.py")
os.system(f"{python} 3b_report_NU.py")
os.system(f"{python} 3c_plotphotomstars_NU.py")
os.system(f"{python} 5_histo_multifield_NU.py")
os.system(f"{python} 6_facult_merge_pdf_NU.py")