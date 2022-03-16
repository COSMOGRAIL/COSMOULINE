import os

os.system('python 1_prepare.py')
os.system('python 2a_extract_NU.py')
os.system('python 2b_facult_applymasks_NU.py')
os.system('python 3_facult_findcosmics_NU.py')
os.system('python 4_buildpsf_NU.py')
os.system('python 5_pngcheck_NU.py')
