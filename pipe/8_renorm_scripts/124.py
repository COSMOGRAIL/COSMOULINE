import os
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from variousfct import *

os.system("python3 1a_renormalize.py")
os.system("python3 1b_report_NU.py")
os.system("python3 2_plot_star_curves_NU.py")
os.system("python3 4_fac_merge_pdf_NU.py")