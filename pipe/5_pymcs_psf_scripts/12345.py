import os

os.system('python3 1_prepare.py')
os.system('python3 2a_extract_NU.py')
os.system('python3 2b_facult_applymasks_NU.py')
os.system('python3 3_facult_findcosmics_NU.py')
os.system('python3 4_buildpsf_NU.py')
os.system('python3 5_pngcheck_NU.py')
