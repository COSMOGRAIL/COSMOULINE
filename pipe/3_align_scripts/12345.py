import os
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
from variousfct import *

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
