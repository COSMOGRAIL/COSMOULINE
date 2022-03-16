execfile("../config.py")
import os
from kirbybase import KirbyBase, KBError
from variousfct import *
from headerstuff import *


print "I will update the database with new images in set %s, telescope %s from %s" %(setname, telescopename, rawdir)
print ""
db = KirbyBase()
images = db.select(imgdb, ['gogogo','treatme','updating'], [True, True, True], returnType='dict')
nbrofimages = len(images)
print "Number of images to treat :", nbrofimages
proquest(askquestions)

os.chdir('../5_pymcs_psf_scripts')
os.system('python 1_prepare.py')
os.system('python 2a_extract_NU.py')
os.system('python 2b_facult_applymasks_NU.py')
os.system('python 3_facult_findcosmics_NU.py')
os.system('python 4_buildpsf_NU.py')
os.system('python 5_pngcheck_NU.py')
os.system('python 6_checkfiles_NU.py')
os.system('python 7_fac_listsaturated_NU.py')
os.system('python 6b_handcheck_psf_NU.py')

