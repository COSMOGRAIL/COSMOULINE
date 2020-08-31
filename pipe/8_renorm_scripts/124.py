import os
execfile("../config.py")
from variousfct import *

os.system("python 1a_renormalize.py")
os.system("python 1b_report_NU.py")
os.system("python 2_plot_star_curves_NU.py")
os.system("python 4_fac_merge_pdf_NU.py")