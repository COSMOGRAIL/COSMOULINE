import os

exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
os.system("python3 1b_copyconvert_NU.py")
os.system("python3 1c_report_NU.py")
os.system("python3 2a_astrocalc.py")
os.system("python3 3a_runsex_NU.py")
os.system("python3 3b_measureseeing.py")
os.system("python3 3c_report_NU.py")
os.system("python3 4a_skystats.py")
os.system("python3 4b_report_NU.py")
