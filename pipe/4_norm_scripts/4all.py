import os
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))

os.system(f"{python} 4a_fac_prepcombi_NU.py")
os.system(f"{python} 4b_fac_combibest_NU.py")
os.system(f"{python} 4c_fac_makecombipngmap_NU.py")