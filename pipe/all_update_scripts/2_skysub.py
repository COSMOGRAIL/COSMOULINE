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
defringed = settings['defringed']

print(f"I will update the database with new images in sets {setnames},"
      f"telescope {telescopename}")
print("Note that I will use the normal sky substraction")
print("")
db = KirbyBase(imgdb)
images = db.select(imgdb, ['gogogo','treatme','updating'], 
                          [True, True, True], 
                          returnType='dict')
nbrofimages = len(images)
print("Number of images to treat :", nbrofimages)
proquest(askquestions)

os.chdir('../2_skysub_scripts')
try:
	os.system(f'{python} 1_skysub_NU.py')
except:
	print("Problem with script 1")
	sys.exit()

if defringed:
	os.system(f'{python} 1b_compute_fringes.py')

try:
	os.system(f'{python} 2_skypng_NU.py')
except:
	print("Problem with script 2")
	sys.exit()


print("Sky substraction done!")
