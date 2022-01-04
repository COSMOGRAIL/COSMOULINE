import os

os.system(f'{python} 1_prepare.py')
os.system(f'{python} 2a_extract_NU.py')
os.system(f'{python} 2b_facult_applymasks_NU.py')
os.system(f'{python} 3_facult_findcosmics_NU.py')
os.system(f'{python} 4_buildpsf_NU.py')
os.system(f'{python} 5_pngcheck_NU.py')
