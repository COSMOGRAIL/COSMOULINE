import os

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
os.system("python3 4a_fac_prepcombi_NU.py")
os.system("python3 4b_fac_combibest_NU.py")
os.system("python3 4c_fac_makecombipngmap_NU.py")