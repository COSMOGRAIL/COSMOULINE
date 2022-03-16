import os
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from variousfct import *

os.system(f"{python} 1a_renormalize.py")
os.system(f"{python} 1b_report_NU.py")
os.system(f"{python} 2_plot_star_curves_NU.py")
os.system(f"{python} 4_fac_merge_pdf_NU.py")