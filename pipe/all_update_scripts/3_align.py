exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
import os
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *


print("I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir))
print("Note that I will use the normal sky substraction")
print("")
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)


os.chdir('../3_align_scripts')
os.system(f'{python} 0a_to_2a_align_in_one_step.py')
os.system(f'{python} 2b_report_NU.py')
os.system(f'{python} 3_updateflags.py')
os.system(f'{python} 4_pngcheck_NU.py')

print("Alignment done!")
