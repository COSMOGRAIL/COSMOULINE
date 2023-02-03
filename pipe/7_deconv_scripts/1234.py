import os
exec (open("../config.py").read())

# os.system(f"{python} 0_facult_autoskiplist_NU.py")
os.system(f"{python} 1_prepfiles.py")
os.system(f"{python} 2_applynorm_NU.py")
os.system(f"{python} 3_fillinfile_NU.py")
os.system(f"{python} 4_deconv_NU.py")
os.system(f"{python} 5b_showptsrc_NU.py")
os.system(f"{python} 5a_decpngcheck_NU.py")
