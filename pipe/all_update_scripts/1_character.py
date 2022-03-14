import glob
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

telescopename = settings['telescopename']
setnames = settings['setnames']
rawdirs = settings['rawdirs']

print("I will update the database with new images, with",
      f"telescope {telescopename}\n")

for setname, rawdir in zip(setnames, rawdirs):
    nimages = len(glob.glob(os.path.join(rawdir, "*.fits")))
    db = KirbyBase(imgdb)
    images = db.select(imgdb, ['recno'], ['*'],['setname'], returnType='dict')
    nimagesindb = len([image for image in images if image['setname'] == setname])
    print(f"I have {int(nimagesindb)} images in the database for set {setname}")
    print(f"I have found {int(nimages)} images in the your raw folder")
    if nimages > nimagesindb :
    	nnewimages = nimages-nimagesindb
    	print(f"This means {int(nnewimages)} new images added to this set")
    else :
    	nnewimages = nimages
    	print("It seems that you have only the new images in the raw folder,",
              f"I will add {int(nimages)} new images.")
    
    if nnewimages == 0:
    	print("Nothing to do.")
    	#sys.exit()

proquest(settings['askquestions'])

os.chdir('../1_character_scripts')
try:
	os.system(f'{python} 1a_addtodatabase.py')
except:
	print("Problem with script 1a")
	sys.exit()
try:
	os.system(f'{python} 1b_copyconvert_NU.py')
except:
	print("Problem with script 1b ")
	sys.exit()
try:
	os.system(f'{python} 1c_report_NU.py')
except:
	print("Problem with script 1c")
	sys.exit()
try:
	os.system(f'{python} 2a_astrocalc.py')
except:
	print("Problem with script 2a")
	sys.exit()
try:
	os.system(f'{python} 2b_report_NU.py')
except:
	print("Problem with script 2b")
	sys.exit()
try:
	os.system(f'{python} 3a_runsex_NU.py')
except:
	print("Problem with script 3a")
	sys.exit()
try:
	os.system(f'{python} 3b_measureseeing.py')
except:
	print("Problem with script 3b")
	sys.exit()
try:
	os.system(f'{python} 3c_report_NU.py')
except:
	print("Problem with script 3c")
	sys.exit()
try:
	os.system(f'{python} 4a_skystats.py')
except:
	print("Problem with script 4a")
	sys.exit()
try:
	os.system(f'{python} 4b_report_NU.py')
except:
	print("Problem with script 4b")
	sys.exit()

print("Done with characterisation !")