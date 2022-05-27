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
