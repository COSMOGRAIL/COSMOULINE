import os
python = "/home/fred/anaconda3/bin/python"
exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
os.system(f"{python} 1b_copyconvert_NU.py")
os.system(f"{python} 1c_report_NU.py")
os.system(f"{python} 2a_astrocalc.py")
os.system(f"{python} 3a_runsex_NU.py")
os.system(f"{python} 3b_measureseeing.py")
os.system(f"{python} 3c_report_NU.py")
os.system(f"{python} 4a_skystats.py")
os.system(f"{python} 4b_report_NU.py")
