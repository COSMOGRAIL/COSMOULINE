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
from modules.variousfct import proquest

os.system(f"{python} 1a_checkalistars_NU.py")
os.system(f"{python} 1b_identcoord.py")
os.system(f"{python} 1c_report_NU.py")
os.system(f"{python} 2a_alignimages.py")
os.system(f"{python} 2b_report.py")
os.system(f"{python} 3_updateflags.py")
os.system(f"{python} 4_pngcheck_NU.py")
print("I can remove the non aligned images.")
proquest(True)
os.system(f"{python} 5_facult_rm_nonalifits_NU.py")
