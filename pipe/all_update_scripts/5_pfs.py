import sys
import os
if sys.path[0]:
    # if ran as a script, append the parent dir to the path
    sys.path.append(os.path.dirname(sys.path[0]))
else:
    # if ran interactively, append the parent manually as sys.path[0] 
    # will be emtpy.
    sys.path.append('..')
from config import imgdb, settings, python
from modules.variousfct import proquest
from modules.kirbybase import KirbyBase

setnames = settings['setnames']
telescopename = settings['telescopename']
askquestions = settings['askquestions']


print(f"I will update the database with new images in set {setnames},"
      f"telescope {telescopename}")
print("")

db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo','treatme','updating'], 
                          [True, True, True], 
                          returnType='dict')
nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)

os.chdir('../5_pymcs_psf_scripts')
os.system(f'{python} 1_prepare.py')
os.system(f'{python} 2a_extract_NU.py')
os.system(f'{python} 2b_facult_applymasks_NU.py')
os.system(f'{python} 3_facult_findcosmics_NU.py')
os.system(f'{python} 4_buildpsf_NU.py')
os.system(f'{python} 5_pngcheck_NU.py')
os.system(f'{python} 6_checkfiles_NU.py')
os.system(f'{python} 7_fac_listsaturated_NU.py')
os.system(f'{python} 6b_handcheck_psf_NU.py')

