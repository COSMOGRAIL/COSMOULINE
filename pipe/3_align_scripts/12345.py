import os
execfile("../config.py")
from variousfct import *

os.system("python 1a_checkalistars_NU.py")
os.system("python 1b_identcoord.py")
os.system("python 1c_report_NU.py")
os.system("python 2a_multicpu_alignimages.py")
os.system("python 2b_report.py")
os.system("python 3_updateflags.py")
os.system("python 4_pngcheck_NU.py")
print "I can remove the non aligned images."
proquest(True)
os.system("python 5_facult_rm_nonalifits_NU.py")
