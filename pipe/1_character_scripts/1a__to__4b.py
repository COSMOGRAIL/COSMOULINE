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

os.system(f"{python} 1a_addtodatabase.py")
os.system(f"{python} 1b_copyconvert_NU.py")
os.system(f"{python} 1c_report_NU.py")
os.system(f"{python} 2a_astrocalc.py")
os.system(f"{python} 3a_runsex_NU.py")
os.system(f"{python} 3b_measureseeing.py")
os.system(f"{python} 3c_report_NU.py")
os.system(f"{python} 4a_skystats.py")
os.system(f"{python} 4b_report_NU.py")
