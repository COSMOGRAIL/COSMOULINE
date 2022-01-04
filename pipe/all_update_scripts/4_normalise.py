exec(compile(open("../config.py", "rb").read(), "../config.py", 'exec'))
import os,sys
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


os.chdir('../4_norm_scripts')
os.system(f'{python} 1a_imstat.py')
os.system(f'{python} 1b_facult_fillnoise_NU.py')
os.system(f'{python} 2a_runsex_NU.py')
os.system(f'{python} 2b_facult_photomdb.py')
os.system(f'{python} 2c_facult_peakdb.py')
os.system(f'{python} 2d_facult_plotpeakadu_NU.py')
os.system(f'{python} 3a_calccoeff.py')
os.system(f'{python} 3b_report_NU.py')
os.system(f'{python} 3c_plotphotomstars_NU.py')
os.system(f'{python} 5_histo_multifield_NU.py')