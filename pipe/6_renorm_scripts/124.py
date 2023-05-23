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

os.system(f"{python} 1a_renormalize.py")
os.system(f"{python} 1b_report_NU.py")
os.system(f"{python} 2_plot_star_curves_NU.py")
os.system(f"{python} 4_fac_merge_pdf_NU.py")
